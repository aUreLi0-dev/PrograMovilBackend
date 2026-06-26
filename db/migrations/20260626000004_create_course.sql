-- migrate:up

CREATE TABLE course (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    default_credit INTEGER NOT NULL,
    origin_faculty VARCHAR(120),
    CONSTRAINT chk_course_default_credit CHECK (default_credit > 0)
);

-- migrate:down

DROP TABLE IF EXISTS course;
