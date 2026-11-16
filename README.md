# Lab 4: Search Queries in SQL (Part II, Problem 2: Library)

**Students:**

- Sohila Wael, ID 2304073

- Omar Mohamed, ID 2304093

This repository contains **Problem 2** of Lab 4: the library database with six tables (AUTHOR, PUBLISHER, CATEGORY, BOOK, MEMBER, LOAN), its seed data, the SQL of the search pages, and the website with the new search pages. The website continues the Lab 3 / Lab 2 website (Flask + MySQL). The Lab 2 README is kept at the end of this file.

## Folder structure

```

lab4-2304098/

  problem2_DDL.sql        # library database: 6 tables, primary keys, foreign keys, ON DELETE CASCADE

  problem2_DML.sql        # seed data: 5 authors, 3 publishers, 3 categories, 10 books, 5 members, 12 loans

  problem2_Queries.sql    # the SQL of the pages F2.1 to F2.6 (with a comment -- F2.x before each query)

  website/                # Lab 2/3 website + the new search pages

    app.py

    requirements.txt

    .env.example

    templates/            # Lab 2/3 pages + search, catalogue, reports, loans, most_borrowed, authors_books

    static/               # style.css and static/uploads (book covers and author photos)

    database/schema.sql   # Lab 2 database (`registration`), needed only for the login / to-do pages

  README.md

```

## Requirements

- MySQL Server 8 (and the `mysql` command-line client)

- Python 3.10 or newer

## Step 1: Build the library database

Open the **MySQL Command Line Client** (or run `mysql -u root -p` in a terminal) and run the scripts in this order. Use the full path of the folder, with `/` slashes:

```

source C:/path/to/lab4-2304098/problem2_DDL.sql

source C:/path/to/lab4-2304098/problem2_DML.sql

```

`problem2_DDL.sql` starts with `DROP DATABASE IF EXISTS library; CREATE DATABASE library; USE library;`, so it can be re-run at any time. Run the DDL before the DML.

> On Linux/macOS or Windows CMD you can also run `mysql -u root -p < problem2_DDL.sql`.

> This does not work in PowerShell, use `source` as above.

## Step 2: Run the queries of the pages (optional)

```

source C:/path/to/lab4-2304098/problem2_Queries.sql

```

Every query has a comment `-- F2.1`, `-- F2.2`, ... before it. F2.1 appears twice: the plain query, and the bonus version written as a prepared statement (`PREPARE` / `EXECUTE`).

## Step 3: Lab 2 database (login and to-do pages, optional)

The website still contains the Lab 2 pages (register, login, to-do list), which use the database `registration`. Only these pages need it; the library pages do not need a login.

```

source C:/path/to/lab4-2304098/website/database/schema.sql

```

## Step 4: Run the website

Open a terminal in the `website` folder and create the virtual environment:

```

cd website

python -m venv venv

venv\Scripts\activate          # Linux/macOS: source venv/bin/activate

pip install -r requirements.txt

```

Copy `.env.example` to `.env` (`copy .env.example .env` on Windows, `cp .env.example .env` on Linux/macOS) and fill in your values: your MySQL password and a long random `SECRET_KEY`:

```

SECRET_KEY=any-long-random-text

DB_HOST=localhost

DB_USER=root

DB_PASSWORD=your_mysql_password

DB_NAME=registration

```

`DB_NAME` is the Lab 2 database. The library pages connect to the database `library` automatically, with the same host, user and password.

Start the server:

```

python app.py

```

Open **http://127.0.0.1:5000/books/search** in the browser. The menu at the top of every library page links to all the other pages.

## Website pages (Problem 2)

| Requirement | Page | SQL features |

|---|---|---|

| F2.1 Search books: title keyword, minimum / maximum price, category; cheapest first | `/books/search` | WHERE, LIKE, BETWEEN, ORDER BY |

| F2.2 Catalogue with author, publisher and category names | `/catalogue` | JOIN of 4 tables |

| F2.3 Reports: (a) books and average price per category, (b) authors with at least 2 books, (c) total / smallest / largest price | `/reports` | GROUP BY, HAVING, COUNT, AVG, SUM, MIN, MAX |

| F2.4 Loans: (a) not returned yet, (b) members who never borrowed, (c) books never borrowed | `/loans` | JOIN, LEFT JOIN ... IS NULL |

| F2.5 Most borrowed: the 3 books with the most loans, the member with the most loans | `/most-borrowed` | GROUP BY, ORDER BY, LIMIT |

| F2.6 Authors and books: (a) every author with the number of books (0 included), (b) books whose author and publisher are from the same country | `/authors-books` | LEFT JOIN, JOIN |

The Lab 3 page `/library` (add, edit and delete books and authors, with images) is kept. Because the table BOOK has new columns, its book forms now also ask for the publish year, the publisher and the category.

## Bonus: prepared statements in F2.1

The search form never builds the SQL text with what the user typed. The statement `SEARCH_SQL` in `app.py` is a fixed text with `?` placeholders:

```sql

WHERE b.title LIKE CONCAT('%', ?, '%')

  AND b.price BETWEEN ? AND ?

  AND (? = 0 OR b.category_id = ?)

```

It is run with `mysql.connector` and `cursor(prepared=True)`, which is a real server-side prepared statement: MySQL first receives and parses the SQL text, and the keyword, the prices and the category are sent afterwards as separate values. A keyword such as `' OR 1=1 --` is therefore only text to search for and cannot change the query. The `%` and `_` typed by the user are also escaped, so they are normal characters and not wildcards. An empty keyword matches every title, an empty price box means "no limit", and category 0 means "all categories". The same idea is shown in `problem2_Queries.sql` with `PREPARE ... EXECUTE ... USING`.

---

# Lab 2: Login & To-Do Application (previous assignment, kept in this README)

The Lab 2 pages are still part of the website (`/register`, `/login`, `/logout`, `/todos`). To run them, follow Steps 3 and 4 above and open `http://127.0.0.1:5000/register`.

## 1. Team Members

### Student 1

- Name: Sohila Wael

- ID: 2304073

- Wrote `database/schema.sql` (both tables and the foreign key).

- R1: Register with a duplicate e-mail check (`Email Already Exists`).

- R2: Login with the same message for a wrong e-mail or password, and logout.

- R3: Private list; redirect to the login page when not logged in.

- R9: bcrypt password hashing, parameterized queries, `user_id` from the session.

- R8 (part): validation of the register and login forms in the browser and on the server.

- Screenshots and README sections.

### Student 2

- Name: Omar Mohamed

- ID: 2304093

- R4 to R7: add, edit, mark done/not done, delete (with confirmation), using `AND user_id = ?`.

- R8 (part): validation of the to-do title in the browser and on the server.

- R10: consistent styling, 360 px responsive layout, empty-list message, done state.

- Bonus: counter of open to-dos.

## 2. Technology

- Back end: Python 3 with Flask. Passwords are hashed with `bcrypt`. MySQL is accessed with `PyMySQL` using plain SQL with parameters (no ORM).

- Front end: HTML, CSS and JavaScript, with Jinja templates.

- Database: MySQL 8.0, database `registration`.

## 3. Features

- R1 = Register with name, e-mail, password and confirm password. A duplicate e-mail shows `Email Already Exists`. After registering, the user is logged in and sees the list.

- R2 = Login with e-mail and password. A wrong e-mail or a wrong password shows the same message, `Invalid email or password`. Logout ends the session.

- R3 = The list is private. A visitor who is not logged in is redirected to the login page, and each user sees only their own to-dos, newest first.

- R4 = Add a to-do.

- R5 = Edit a to-do title.

- R6 = Mark a to-do as done or not done.

- R7 = Delete a to-do, with an "Are you sure?" confirmation.

- R8 = Validation in the browser (JavaScript) and again on the server, with the exact messages from the lab.

- R9 = Passwords are stored as bcrypt hashes. Only the given queries are used, always with parameters, and `user_id` always comes from the session.

- R10 = A consistent, responsive interface that works on a 360 px screen, with error messages, a visible state for done to-dos, an empty-list message, and the user's name with a logout button.

- Bonus: counter showing how many to-dos are still open.

## 4. Screenshots

The Lab 2 screenshots are in the `screenshots` folder of the Lab 2 repository:

https://github.com/sohilawael32-crypto/-Login-To-Do-Application-lab2

## 5. Answers

**(a) Why do UPDATE and DELETE contain `AND user_id = ?`, and what changes if you remove it?**

The id of a to-do comes from the browser, so anybody can send somebody else's number. Adding `AND user_id = ?` (the id of the logged-in user, taken from the session and never from a form) makes the statement change zero rows when the to-do is not yours. Without it, any logged-in user could edit or delete another user's to-dos just by changing the number in the request.

**(b) What happens if you insert a to-do for a `user_id` that does not exist, and which constraint of the lecture is that?**

MySQL rejects the INSERT with error 1452: "Cannot add or update a child row: a foreign key constraint fails". This is the foreign key constraint (referential integrity): every to-do must belong to exactly one existing user.

**(c) Why do you store a hash and not the password?**

If the database is leaked, anyone who reads it would see all the real passwords. A bcrypt hash cannot be reversed to get the original password. It is also salted, so two users with the same password get different hashes, and it is slow on purpose, which makes guessing attacks expensive. To log in, the library compares the typed password with the stored hash (`bcrypt.checkpw`).

**(d) The `name` column is NOT NULL: why did you still need your own check for an empty name?**

`NOT NULL` only means that the column must have a value. An empty text `''` is a value, not NULL, so MySQL accepts it. Only our own checks (in JavaScript in the browser and again on the server) can refuse an empty name.
