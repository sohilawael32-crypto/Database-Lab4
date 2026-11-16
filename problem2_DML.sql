USE library;

-- Parents first (BOOK and LOAN refer to them)
INSERT INTO AUTHOR (author_id, name, country) VALUES
(1, 'Naguib Mahfouz',  'Egypt'),          -- 1 and 4: two authors from the same country (Egypt)
(2, 'Agatha Christie', 'United Kingdom'),
(3, 'Paulo Coelho',    'Brazil'),
(4, 'Taha Hussein',    'Egypt'),
(5, 'Elif Shafak',     'Turkey');         -- an author with no books

INSERT INTO PUBLISHER (publisher_id, name, country) VALUES
(1, 'Dar El Shorouk',  'Egypt'),          -- same country as the authors 1 and 4
(2, 'HarperCollins',   'United Kingdom'), -- same country as the author 2
(3, 'Editora Rocco',   'Brazil');         -- same country as the author 3

INSERT INTO CATEGORY (category_id, name) VALUES
(1, 'Fiction'),
(2, 'Mystery'),
(3, 'Autobiography');

-- (book_id, title, price, publish_year, author_id, publisher_id, category_id)
INSERT INTO BOOK (book_id, title, price, publish_year, author_id, publisher_id, category_id) VALUES
(1,  'Palace Walk',                       150.00, 1956, 1, 1, 1),
(2,  'Midaq Alley',                       120.50, 1947, 1, 1, 1),
(3,  'Murder on the Orient Express',      180.00, 1934, 2, 2, 2),
(4,  'And Then There Were None',          165.75, 1939, 2, 2, 2),  -- never borrowed
(5,  'The Alchemist',                     140.00, 1988, 3, 3, 1),
(6,  'Eleven Minutes',                    130.00, 2003, 3, 3, 1),
(7,  'The Days',                          110.00, 1929, 4, 1, 3),
(8,  'The Mysterious Affair at Styles',    18.50, 1920, 2, 2, 2),  -- price between 15 and 20
(9,  'Adrift on the Nile',                 95.00, 1966, 1, 2, 1),  -- Egyptian author, British publisher
(10, 'Brida',                             125.00, 1990, 3, 2, 1);  -- never borrowed; Brazilian author, British publisher

INSERT INTO MEMBER (member_id, name, email, join_date) VALUES
(1, 'Ahmed Hassan',  'ahmed.hassan@example.com', '2026-01-10'),
(2, 'Mona Adel',     'mona.adel@example.com',    '2026-02-03'),
(3, 'Karim Samy',    'karim.samy@example.com',   '2026-03-15'),
(4, 'Laila Nabil',   'laila.nabil@example.com',  '2026-05-21'),
(5, 'Youssef Fathy', 'youssef.fathy@example.com','2026-08-30');   -- a member with no loans

-- (loan_id, book_id, member_id, loan_date, return_date); return_date NULL = not returned yet
INSERT INTO LOAN (loan_id, book_id, member_id, loan_date, return_date) VALUES
(1,  1, 1, '2026-09-01', '2026-09-15'),
(2,  1, 2, '2026-09-10', '2026-09-24'),
(3,  1, 3, '2026-10-05', NULL),          -- not returned yet
(4,  3, 1, '2026-09-20', '2026-10-04'),
(5,  3, 2, '2026-10-12', '2026-10-26'),
(6,  5, 1, '2026-10-02', '2026-10-16'),
(7,  5, 4, '2026-10-18', NULL),          -- not returned yet
(8,  2, 1, '2026-10-20', '2026-11-03'),
(9,  9, 2, '2026-11-01', NULL),          -- not returned yet
(10, 6, 3, '2026-08-15', '2026-08-29'),
(11, 7, 4, '2026-09-05', '2026-09-19'),
(12, 8, 1, '2026-11-02', '2026-11-09');
