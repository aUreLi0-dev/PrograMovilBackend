-- migrate:up

CREATE TABLE syllabus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_offering_id INTEGER NOT NULL UNIQUE REFERENCES course_offering(id),
    title VARCHAR(150),
    drive_file_id VARCHAR(120) NOT NULL UNIQUE,
    drive_file_url VARCHAR(255) NOT NULL
);

-- migrate:down

DROP TABLE IF EXISTS syllabus;
