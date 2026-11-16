DROP DATABASE IF EXISTS library;
CREATE DATABASE library;
USE library;

-- The three "parent" tables are created first, because BOOK and LOAN refer to them.
CREATE TABLE AUTHOR (
  author_id INT          NOT NULL AUTO_INCREMENT,
  name      VARCHAR(100) NOT NULL,
  country   VARCHAR(50),
  PRIMARY KEY (author_id)
);

CREATE TABLE PUBLISHER (
  publisher_id INT          NOT NULL AUTO_INCREMENT,
  name         VARCHAR(100) NOT NULL,
  country      VARCHAR(50),
  PRIMARY KEY (publisher_id)
);

CREATE TABLE CATEGORY (
  category_id INT          NOT NULL AUTO_INCREMENT,
  name        VARCHAR(50)  NOT NULL,
  PRIMARY KEY (category_id)
);

CREATE TABLE BOOK (
  book_id      INT           NOT NULL AUTO_INCREMENT,
  title        VARCHAR(150)  NOT NULL,
  price        DECIMAL(10,2) NOT NULL,
  publish_year SMALLINT      NOT NULL,
  author_id    INT           NOT NULL,
  publisher_id INT           NOT NULL,
  category_id  INT           NOT NULL,
  PRIMARY KEY (book_id),
  FOREIGN KEY (author_id)    REFERENCES AUTHOR(author_id)
    ON DELETE CASCADE,          -- deleting an author deletes all of his/her books (as in Lab 3)
  FOREIGN KEY (publisher_id) REFERENCES PUBLISHER(publisher_id),
  FOREIGN KEY (category_id)  REFERENCES CATEGORY(category_id)
);

CREATE TABLE MEMBER (
  member_id INT          NOT NULL AUTO_INCREMENT,
  name      VARCHAR(100) NOT NULL,
  email     VARCHAR(150) NOT NULL,
  join_date DATE         NOT NULL,
  PRIMARY KEY (member_id),
  UNIQUE (email)
);

CREATE TABLE LOAN (
  loan_id     INT  NOT NULL AUTO_INCREMENT,
  book_id     INT  NOT NULL,
  member_id   INT  NOT NULL,
  loan_date   DATE NOT NULL,
  return_date DATE NULL,        -- NULL while the book is still borrowed
  PRIMARY KEY (loan_id),
  FOREIGN KEY (book_id)   REFERENCES BOOK(book_id)
    ON DELETE CASCADE,          -- deleting a book deletes its loans
  FOREIGN KEY (member_id) REFERENCES MEMBER(member_id)
);
