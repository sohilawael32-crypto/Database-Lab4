import os
import bcrypt
import pymysql
import mysql.connector          # only for the prepared statement of the search page (Lab 4 bonus)
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session
load_dotenv() 
from decimal import Decimal, InvalidOperation
from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


def get_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor,
    )


@app.route("/")
def home():
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS n FROM users")
        row = cur.fetchone()
    db.close()
    return f"Connected! Users in DB: {row['n']}"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm_password", "")

    errors = []
    if not name:
        errors.append("Name is required")
    if not email:
        errors.append("Email is required")
    if not password:
        errors.append("Password is required")
    if not confirm:
        errors.append("Confirm password is required")
    if password and confirm and password != confirm:
        errors.append("Passwords do not match")

    if errors:
        return render_template("register.html", errors=errors, name=name, email=email)

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO users (email, name, password_hash) VALUES (%s, %s, %s)",
                (email, name, hashed),
            )
            user_id = cur.lastrowid
        db.commit()
    except pymysql.err.IntegrityError:
        return render_template("register.html", errors=["Email Already Exists"],
                               name=name, email=email)
    finally:
        db.close()

    session["user_id"] = user_id
    session["name"] = name
    return redirect("/todos")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    errors = []
    if not email:
        errors.append("Email is required")
    if not password:
        errors.append("Password is required")
    if errors:
        return render_template("login.html", errors=errors, email=email)

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT user_id, name, password_hash FROM users WHERE email = %s",
                (email,),
            )
            user = cur.fetchone()
    finally:
        db.close()

    if user is None or not bcrypt.checkpw(
        password.encode("utf-8"), user["password_hash"].encode("utf-8")
    ):
        return render_template("login.html", errors=["Invalid email or password"],
                               email=email)

    session["user_id"] = user["user_id"]
    session["name"] = user["name"]
    return redirect("/todos")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


def validate_title(title):
    if not title.strip():
        return "Title is required"
    if len(title) > 200:
        return "Title is too long (200 characters at most)"
    return None


def show_list(errors=None, new_title=None):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT todo_id, title, is_done, created_at FROM todos "
                "WHERE user_id = %s ORDER BY todo_id DESC",
                (session["user_id"],),
            )
            items = cur.fetchall()
    finally:
        db.close()
    return render_template("todos.html", name=session["name"], todos=items,
                           errors=errors, new_title=new_title)


@app.route("/todos")
def todos():
    if "user_id" not in session:
        return redirect("/login")
    return show_list()


@app.route("/todos/add", methods=["POST"])
def add_todo():
    if "user_id" not in session:
        return redirect("/login")
    title = request.form.get("title", "").strip()
    error = validate_title(title)
    if error:
        return show_list(errors=[error], new_title=title)

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("INSERT INTO todos (user_id, title) VALUES (%s, %s)",
                        (session["user_id"], title))
        db.commit()
    finally:
        db.close()
    return redirect("/todos")


@app.route("/todos/<int:todo_id>/edit", methods=["POST"])
def edit_todo(todo_id):
    if "user_id" not in session:
        return redirect("/login")
    title = request.form.get("title", "").strip()
    error = validate_title(title)
    if error:
        return show_list(errors=[error])

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("UPDATE todos SET title = %s WHERE todo_id = %s AND user_id = %s",
                        (title, todo_id, session["user_id"]))
        db.commit()
    finally:
        db.close()
    return redirect("/todos")


@app.route("/todos/<int:todo_id>/toggle", methods=["POST"])
def toggle_todo(todo_id):
    if "user_id" not in session:
        return redirect("/login")
    is_done = 1 if request.form.get("is_done") == "1" else 0

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("UPDATE todos SET is_done = %s WHERE todo_id = %s AND user_id = %s",
                        (is_done, todo_id, session["user_id"]))
        db.commit()
    finally:
        db.close()
    return redirect("/todos")


@app.route("/todos/<int:todo_id>/delete", methods=["POST"])
def delete_todo(todo_id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("DELETE FROM todos WHERE todo_id = %s AND user_id = %s",
                        (todo_id, session["user_id"]))
        db.commit()
    finally:
        db.close()
    return redirect("/todos")

# ====================== Lab 3: Library (Books and Authors) + image bonus ======================

# ---------- images (bonus) ----------
# Images are saved as files: static/uploads/books/<book_id>.<ext>
#                            static/uploads/authors/<author_id>.<ext>
# The database tables are not changed.
UPLOAD_ROOT = os.path.join(app.root_path, "static", "uploads")
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp"}
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB at most per request

for _kind in ("books", "authors"):
    os.makedirs(os.path.join(UPLOAD_ROOT, _kind), exist_ok=True)


@app.errorhandler(413)
def too_large(e):
    return "The image is too large (5 MB at most). Go back and choose a smaller image.", 413


def image_url(kind, item_id):
    """Returns the url of the image of this book/author, or None if it has no image."""
    for ext in ALLOWED_EXT:
        path = os.path.join(UPLOAD_ROOT, kind, f"{item_id}.{ext}")
        if os.path.exists(path):
            return url_for("static", filename=f"uploads/{kind}/{item_id}.{ext}",
                           v=int(os.path.getmtime(path)))
    return None


app.jinja_env.globals["image_url"] = image_url


def image_error(file):
    """Checks the uploaded file (before touching the database). None = ok or no file chosen."""
    if file is None or file.filename == "":
        return None
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXT:
        return "Image must be png, jpg, jpeg, gif or webp"
    return None


def remove_image(kind, item_id):
    for ext in ALLOWED_EXT:
        path = os.path.join(UPLOAD_ROOT, kind, f"{item_id}.{ext}")
        if os.path.exists(path):
            os.remove(path)


def save_image(kind, item_id, file):
    """Saves the uploaded image (already checked by image_error). Replaces the old image."""
    if file is None or file.filename == "":
        return
    ext = file.filename.rsplit(".", 1)[-1].lower()
    remove_image(kind, item_id)
    file.save(os.path.join(UPLOAD_ROOT, kind, f"{item_id}.{ext}"))


# ---------- database ----------
def get_library_db():
    # same MySQL server and user as Lab 2, but a different database: `library`
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("LIBRARY_DB_NAME", "library"),
        cursorclass=pymysql.cursors.DictCursor,
    )


def validate_author(name, country):
    errors = []
    if not name:
        errors.append("Author name is required")
    elif len(name) > 100:
        errors.append("Author name is too long (100 characters at most)")
    if len(country) > 50:
        errors.append("Country is too long (50 characters at most)")
    return errors


def validate_book(form):
    """form = request.form. Returns (errors, values), values = the cleaned fields of the BOOK table."""
    errors = []
    v = {"title": form.get("title", "").strip()}

    if not v["title"]:
        errors.append("Book title is required")
    elif len(v["title"]) > 150:
        errors.append("Book title is too long (150 characters at most)")

    try:
        v["price"] = Decimal(form.get("price", "").strip())
        if not v["price"].is_finite() or v["price"] < 0 or v["price"] > Decimal("99999999.99"):
            errors.append("Price must be between 0 and 99999999.99")
    except (InvalidOperation, ValueError):
        errors.append("Price must be a number")

    try:
        v["publish_year"] = int(form.get("publish_year", "").strip())
        if not 1 <= v["publish_year"] <= 2100:
            errors.append("Publish year must be between 1 and 2100")
    except ValueError:
        errors.append("Publish year must be a whole number")

    for field, label in (("author_id", "an author"), ("publisher_id", "a publisher"),
                         ("category_id", "a category")):
        try:
            v[field] = int(form.get(field, "").strip())
        except ValueError:
            errors.append("Please choose " + label)

    return errors, v


def get_lookups():
    """The authors, publishers and categories, for the <select> lists."""
    db = get_library_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT author_id, name, country FROM AUTHOR ORDER BY author_id")
            authors = cur.fetchall()
            cur.execute("SELECT publisher_id, name FROM PUBLISHER ORDER BY publisher_id")
            publishers = cur.fetchall()
            cur.execute("SELECT category_id, name FROM CATEGORY ORDER BY category_id")
            categories = cur.fetchall()
        return authors, publishers, categories
    finally:
        db.close()


def show_library(errors=None, form=None):
    db = get_library_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT book_id, title, price, publish_year, author_id, publisher_id, category_id "
                        "FROM BOOK ORDER BY book_id")
            books = cur.fetchall()
    finally:
        db.close()
    authors, publishers, categories = get_lookups()
    return render_template("library.html", books=books, authors=authors, publishers=publishers,
                           categories=categories, errors=errors, form=form or {})


# ---------- F2.1  show both tables ----------
@app.route("/library")
def library():
    return show_library()


# ---------- F2.2  add an author / add a book ----------
@app.route("/authors/add", methods=["POST"])
def add_author():
    name = request.form.get("name", "").strip()
    country = request.form.get("country", "").strip()
    image = request.files.get("image")

    errors = validate_author(name, country)
    img_err = image_error(image)
    if img_err:
        errors.append(img_err)
    if errors:
        return show_library(errors=errors, form={"author_name": name, "author_country": country})

    db = get_library_db()
    try:
        with db.cursor() as cur:
            cur.execute("INSERT INTO AUTHOR (name, country) VALUES (%s, %s)", (name, country or None))
            new_id = cur.lastrowid
        db.commit()
    finally:
        db.close()

    save_image("authors", new_id, image)
    return redirect("/library")


@app.route("/books/add", methods=["POST"])
def add_book():
    image = request.files.get("image")

    errors, v = validate_book(request.form)
    img_err = image_error(image)
    if img_err:
        errors.append(img_err)
    form = {"book_" + k: request.form.get(k, "").strip()
            for k in ("title", "price", "publish_year", "author_id", "publisher_id", "category_id")}
    if errors:
        return show_library(errors=errors, form=form)

    db = get_library_db()
    try:
        with db.cursor() as cur:
            cur.execute("INSERT INTO BOOK (title, price, publish_year, author_id, publisher_id, category_id) "
                        "VALUES (%s, %s, %s, %s, %s, %s)",
                        (v["title"], v["price"], v["publish_year"],
                         v["author_id"], v["publisher_id"], v["category_id"]))
            new_id = cur.lastrowid
        db.commit()
    except pymysql.err.IntegrityError:
        # foreign key failed: this author, publisher or category does not exist
        return show_library(errors=["The author, publisher or category does not exist"], form=form)
    finally:
        db.close()

    save_image("books", new_id, image)
    return redirect("/library")


# ---------- F2.3  edit an author / edit a book ----------
@app.route("/authors/<int:author_id>/edit", methods=["GET", "POST"])
def edit_author(author_id):
    db = get_library_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT author_id, name, country FROM AUTHOR WHERE author_id = %s",
                        (author_id,))
            author = cur.fetchone()
    finally:
        db.close()
    if author is None:
        return redirect("/library")

    if request.method == "GET":
        return render_template("edit_author.html", author=author)

    name = request.form.get("name", "").strip()
    country = request.form.get("country", "").strip()
    image = request.files.get("image")

    errors = validate_author(name, country)
    img_err = image_error(image)
    if img_err:
        errors.append(img_err)
    if errors:
        author["name"], author["country"] = name, country
        return render_template("edit_author.html", author=author, errors=errors)

    db = get_library_db()
    try:
        with db.cursor() as cur:
            cur.execute("UPDATE AUTHOR SET name = %s, country = %s WHERE author_id = %s",
                        (name, country or None, author_id))
        db.commit()
    finally:
        db.close()

    save_image("authors", author_id, image)
    return redirect("/library")


@app.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
def edit_book(book_id):
    db = get_library_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT book_id, title, price, publish_year, author_id, publisher_id, category_id "
                        "FROM BOOK WHERE book_id = %s", (book_id,))
            book = cur.fetchone()
    finally:
        db.close()
    if book is None:
        return redirect("/library")

    authors, publishers, categories = get_lookups()
    lists = dict(authors=authors, publishers=publishers, categories=categories)
    if request.method == "GET":
        return render_template("edit_book.html", book=book, **lists)

    image = request.files.get("image")

    errors, v = validate_book(request.form)
    img_err = image_error(image)
    if img_err:
        errors.append(img_err)
    if errors:
        # show again what the user typed
        for k in ("title", "price", "publish_year"):
            book[k] = request.form.get(k, "").strip()
        for k in ("author_id", "publisher_id", "category_id"):
            if k in v:
                book[k] = v[k]
        return render_template("edit_book.html", book=book, errors=errors, **lists)

    db = get_library_db()
    try:
        with db.cursor() as cur:
            cur.execute("UPDATE BOOK SET title = %s, price = %s, publish_year = %s, author_id = %s, "
                        "publisher_id = %s, category_id = %s WHERE book_id = %s",
                        (v["title"], v["price"], v["publish_year"], v["author_id"],
                         v["publisher_id"], v["category_id"], book_id))
        db.commit()
    except pymysql.err.IntegrityError:
        book["title"], book["price"] = v["title"], v["price"]
        return render_template("edit_book.html", book=book,
                               errors=["The author, publisher or category does not exist"], **lists)
    finally:
        db.close()

    save_image("books", book_id, image)
    return redirect("/library")


# ---------- F2.4 remove a book / F2.5 remove an author ----------
@app.route("/books/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    db = get_library_db()
    try:
        with db.cursor() as cur:
            cur.execute("DELETE FROM BOOK WHERE book_id = %s", (book_id,))
        db.commit()
    finally:
        db.close()

    remove_image("books", book_id)
    return redirect("/library")


@app.route("/authors/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id):
    # ON DELETE CASCADE in the database also deletes all the books of this author,
    # so we remember their ids to delete their cover images too
    db = get_library_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT book_id FROM BOOK WHERE author_id = %s", (author_id,))
            book_ids = [row["book_id"] for row in cur.fetchall()]
            cur.execute("DELETE FROM AUTHOR WHERE author_id = %s", (author_id,))
        db.commit()
    finally:
        db.close()

    for bid in book_ids:
        remove_image("books", bid)
    remove_image("authors", author_id)
    return redirect("/library")

# ====================== end of Lab 3 block ======================


# ====================== Lab 4 (Part II): search pages of the library ======================
# Every page below is a simple SELECT. The same SQL is in problem2_Queries.sql (F2.1 to F2.6).

def run_select(sql):
    """Runs a fixed SELECT (no user input inside) and returns the rows as dictionaries."""
    db = get_library_db()
    try:
        with db.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
    finally:
        db.close()


# ---------- F2.1  Search books (WHERE) + BONUS: prepared statement ----------
# The SQL text is FIXED: it contains only "?" placeholders. What the user typed is never
# added to the text. It is sent to MySQL separately, when the statement is executed
# (mysql.connector with cursor(prepared=True) = real server-side prepared statement).
SEARCH_SQL = """
SELECT b.book_id, b.title, b.price, b.publish_year, a.name AS author, c.name AS category
FROM BOOK b
JOIN AUTHOR a   ON b.author_id   = a.author_id
JOIN CATEGORY c ON b.category_id = c.category_id
WHERE b.title LIKE CONCAT('%', ?, '%')
  AND b.price BETWEEN ? AND ?
  AND (? = 0 OR b.category_id = ?)
ORDER BY b.price ASC, b.title
"""


def search_books(keyword, min_price, max_price, category_id):
    # % and _ typed by the user are normal characters, not wildcards
    keyword = keyword.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("LIBRARY_DB_NAME", "library"),
    )
    try:
        cur = conn.cursor(prepared=True)
        cur.execute(SEARCH_SQL, (keyword, min_price, max_price, category_id, category_id))
        columns = cur.column_names
        rows = [dict(zip(columns, row)) for row in cur.fetchall()]
        cur.close()
        return rows
    finally:
        conn.close()


@app.route("/books/search")
def search_page():
    categories = run_select("SELECT category_id, name FROM CATEGORY ORDER BY name")
    form = {"keyword": request.args.get("keyword", "").strip(),
            "min_price": request.args.get("min_price", "").strip(),
            "max_price": request.args.get("max_price", "").strip(),
            "category_id": request.args.get("category_id", "").strip()}
    searched = bool(request.args)   # false the first time the page is opened
    errors, books = [], None

    if searched:
        min_price, max_price, category_id = Decimal("0"), Decimal("99999999.99"), 0
        try:
            if form["min_price"]:
                min_price = Decimal(form["min_price"])
            if form["max_price"]:
                max_price = Decimal(form["max_price"])
            if not (min_price.is_finite() and max_price.is_finite()):
                raise InvalidOperation
        except InvalidOperation:
            errors.append("Minimum and maximum price must be numbers")
        if not errors and min_price > max_price:
            errors.append("The minimum price must not be greater than the maximum price")
        if len(form["keyword"]) > 150:
            errors.append("The keyword is too long (150 characters at most)")
        if form["category_id"]:
            try:
                category_id = int(form["category_id"])
            except ValueError:
                errors.append("Please choose a category from the list")
        if not errors:
            books = search_books(form["keyword"], min_price, max_price, category_id)

    return render_template("search.html", form=form, categories=categories,
                           books=books, errors=errors)


# ---------- F2.2  Catalogue (JOIN) ----------
@app.route("/catalogue")
def catalogue():
    books = run_select("""
        SELECT b.book_id, b.title, b.price, b.publish_year,
               a.name AS author, p.name AS publisher, c.name AS category
        FROM BOOK b
        JOIN AUTHOR a    ON b.author_id    = a.author_id
        JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
        JOIN CATEGORY c  ON b.category_id  = c.category_id
        ORDER BY b.book_id""")
    return render_template("catalogue.html", books=books)


# ---------- F2.3  Reports (GROUP BY, HAVING) ----------
@app.route("/reports")
def reports():
    per_category = run_select("""
        SELECT c.name AS category, COUNT(b.book_id) AS books, AVG(b.price) AS average_price
        FROM CATEGORY c
        LEFT JOIN BOOK b ON b.category_id = c.category_id
        GROUP BY c.category_id, c.name
        ORDER BY c.name""")
    busy_authors = run_select("""
        SELECT a.name AS author, COUNT(*) AS books
        FROM AUTHOR a
        JOIN BOOK b ON b.author_id = a.author_id
        GROUP BY a.author_id, a.name
        HAVING COUNT(*) >= 2
        ORDER BY books DESC, a.name""")
    totals = run_select("""
        SELECT SUM(price) AS total_price, MIN(price) AS smallest_price, MAX(price) AS largest_price
        FROM BOOK""")[0]
    return render_template("reports.html", per_category=per_category,
                           busy_authors=busy_authors, totals=totals)


# ---------- F2.4  Loans (JOIN, LEFT JOIN) ----------
@app.route("/loans")
def loans():
    not_returned = run_select("""
        SELECT l.loan_id, b.title, m.name AS member, l.loan_date
        FROM LOAN l
        JOIN BOOK b   ON l.book_id   = b.book_id
        JOIN MEMBER m ON l.member_id = m.member_id
        WHERE l.return_date IS NULL
        ORDER BY l.loan_date""")
    no_loans = run_select("""
        SELECT m.member_id, m.name, m.email
        FROM MEMBER m
        LEFT JOIN LOAN l ON l.member_id = m.member_id
        WHERE l.loan_id IS NULL
        ORDER BY m.member_id""")
    never_borrowed = run_select("""
        SELECT b.book_id, b.title
        FROM BOOK b
        LEFT JOIN LOAN l ON l.book_id = b.book_id
        WHERE l.loan_id IS NULL
        ORDER BY b.book_id""")
    return render_template("loans.html", not_returned=not_returned,
                           no_loans=no_loans, never_borrowed=never_borrowed)


# ---------- F2.5  Most borrowed (GROUP BY, ORDER BY, LIMIT) ----------
@app.route("/most-borrowed")
def most_borrowed():
    top_books = run_select("""
        SELECT b.title, COUNT(*) AS loans
        FROM BOOK b
        JOIN LOAN l ON l.book_id = b.book_id
        GROUP BY b.book_id, b.title
        ORDER BY loans DESC, b.title
        LIMIT 3""")
    top_member = run_select("""
        SELECT m.name AS member, COUNT(*) AS loans
        FROM MEMBER m
        JOIN LOAN l ON l.member_id = m.member_id
        GROUP BY m.member_id, m.name
        ORDER BY loans DESC, m.name
        LIMIT 1""")
    return render_template("most_borrowed.html", top_books=top_books, top_member=top_member)


# ---------- F2.6  Authors and books (LEFT JOIN, JOIN) ----------
@app.route("/authors-books")
def authors_books():
    author_counts = run_select("""
        SELECT a.author_id, a.name AS author, COUNT(b.book_id) AS books
        FROM AUTHOR a
        LEFT JOIN BOOK b ON b.author_id = a.author_id
        GROUP BY a.author_id, a.name
        ORDER BY a.author_id""")
    same_country = run_select("""
        SELECT b.book_id, b.title, a.name AS author, p.name AS publisher, a.country
        FROM BOOK b
        JOIN AUTHOR a    ON b.author_id    = a.author_id
        JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
        WHERE a.country = p.country
        ORDER BY b.book_id""")
    return render_template("authors_books.html", author_counts=author_counts,
                           same_country=same_country)

# ====================== end of Lab 4 block ======================

if __name__ == "__main__":
    app.run(debug=True)