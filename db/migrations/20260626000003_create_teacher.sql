-- migrate:up

CREATE TABLE teacher (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_code VARCHAR(50) UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    institutional_email VARCHAR(150) UNIQUE
);

-- migrate:down

DROP TABLE IF EXISTS teacher;
