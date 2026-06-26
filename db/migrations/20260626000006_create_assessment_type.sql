-- migrate:up

CREATE TABLE assessment_type (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(120) NOT NULL UNIQUE,
    abbreviation VARCHAR(30),
    description TEXT
);

-- migrate:down

DROP TABLE IF EXISTS assessment_type;
