USE library;

-- F2.1  Search books (WHERE): title keyword, price range, category; cheapest first.
-- Example values: keyword 'the', price from 100 to 200, category 1 (Fiction).
SELECT b.book_id, b.title, b.price, b.publish_year, a.name AS author, c.name AS category
FROM BOOK b
JOIN AUTHOR a   ON b.author_id   = a.author_id
JOIN CATEGORY c ON b.category_id = c.category_id
WHERE b.title LIKE '%the%'
  AND b.price BETWEEN 100 AND 200
  AND b.category_id = 1
ORDER BY b.price ASC;

-- F2.1  (bonus) the same search as a PREPARED STATEMENT: the SQL text has placeholders (?)
-- and the values typed by the user are sent separately, as in the website.
-- An empty keyword matches every title; category 0 means "all categories".
PREPARE search_books FROM
 'SELECT b.book_id, b.title, b.price, b.publish_year, a.name AS author, c.name AS category
  FROM BOOK b
  JOIN AUTHOR a   ON b.author_id   = a.author_id
  JOIN CATEGORY c ON b.category_id = c.category_id
  WHERE b.title LIKE CONCAT(''%'', ?, ''%'')
    AND b.price BETWEEN ? AND ?
    AND (? = 0 OR b.category_id = ?)
  ORDER BY b.price ASC';
SET @kw = 'the', @min_price = 100, @max_price = 200, @cat = 1;
EXECUTE search_books USING @kw, @min_price, @max_price, @cat, @cat;
DEALLOCATE PREPARE search_books;

-- F2.2  Catalogue (JOIN): author, publisher and category names instead of the ids.
SELECT b.book_id, b.title, b.price, b.publish_year,
       a.name AS author, p.name AS publisher, c.name AS category
FROM BOOK b
JOIN AUTHOR a    ON b.author_id    = a.author_id
JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
JOIN CATEGORY c  ON b.category_id  = c.category_id
ORDER BY b.book_id;

-- F2.3 (a)  Number of books and average price of each category.
SELECT c.name AS category, COUNT(b.book_id) AS books, AVG(b.price) AS average_price
FROM CATEGORY c
LEFT JOIN BOOK b ON b.category_id = c.category_id
GROUP BY c.category_id, c.name
ORDER BY c.name;

-- F2.3 (b)  Authors who wrote at least 2 books.
SELECT a.name AS author, COUNT(*) AS books
FROM AUTHOR a
JOIN BOOK b ON b.author_id = a.author_id
GROUP BY a.author_id, a.name
HAVING COUNT(*) >= 2
ORDER BY books DESC, a.name;

-- F2.3 (c)  Total, smallest and largest price of the whole library.
SELECT SUM(price) AS total_price, MIN(price) AS smallest_price, MAX(price) AS largest_price
FROM BOOK;

-- F2.4 (a)  Loans not returned yet, with the book title and the member name.
SELECT l.loan_id, b.title, m.name AS member, l.loan_date
FROM LOAN l
JOIN BOOK b   ON l.book_id   = b.book_id
JOIN MEMBER m ON l.member_id = m.member_id
WHERE l.return_date IS NULL
ORDER BY l.loan_date;

-- F2.4 (b)  Members who never borrowed a book.
SELECT m.member_id, m.name, m.email
FROM MEMBER m
LEFT JOIN LOAN l ON l.member_id = m.member_id
WHERE l.loan_id IS NULL;

-- F2.4 (c)  Books that were never borrowed.
SELECT b.book_id, b.title
FROM BOOK b
LEFT JOIN LOAN l ON l.book_id = b.book_id
WHERE l.loan_id IS NULL;

-- F2.5 (a)  The 3 books with the most loans.
SELECT b.title, COUNT(*) AS loans
FROM BOOK b
JOIN LOAN l ON l.book_id = b.book_id
GROUP BY b.book_id, b.title
ORDER BY loans DESC, b.title
LIMIT 3;

-- F2.5 (b)  The member with the most loans.
SELECT m.name AS member, COUNT(*) AS loans
FROM MEMBER m
JOIN LOAN l ON l.member_id = m.member_id
GROUP BY m.member_id, m.name
ORDER BY loans DESC, m.name
LIMIT 1;

-- F2.6 (a)  Every author with the number of books he or she wrote (0 included).
SELECT a.author_id, a.name AS author, COUNT(b.book_id) AS books
FROM AUTHOR a
LEFT JOIN BOOK b ON b.author_id = a.author_id
GROUP BY a.author_id, a.name
ORDER BY a.author_id;

-- F2.6 (b)  Books whose author and publisher come from the same country.
SELECT b.book_id, b.title, a.name AS author, p.name AS publisher, a.country
FROM BOOK b
JOIN AUTHOR a    ON b.author_id    = a.author_id
JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
WHERE a.country = p.country
ORDER BY b.book_id;
