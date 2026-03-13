-- DELETE OLD TABLES
DROP TABLE IF EXISTS public.transactions;
DROP TABLE IF EXISTS public.students;
DROP TABLE IF EXISTS public.books;
DROP TABLE IF EXISTS public.admins;

-- BOOKS TABLE
CREATE TABLE public.books (
    id VARCHAR(20) PRIMARY KEY,
    title VARCHAR(200),
    author VARCHAR(200),
    total INT,
    available INT
);

-- STUDENTS TABLE
CREATE TABLE public.students (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(200),
    course VARCHAR(200)
);

-- TRANSACTIONS TABLE
CREATE TABLE public.transactions (
    id SERIAL PRIMARY KEY,
    book_id VARCHAR(20),
    student_id VARCHAR(20),
    action VARCHAR(20),
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ADMINS TABLE
CREATE TABLE public.admins (
    id VARCHAR(20) PRIMARY KEY,
    password VARCHAR(200)
);

-- DEFAULT ADMIN
INSERT INTO public.admins VALUES ('admin','admin123');

-- CHECK ADMIN
SELECT * FROM public.admins;