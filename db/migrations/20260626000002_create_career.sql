-- migrate:up

CREATE TABLE career (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(120) NOT NULL,
    faculty VARCHAR(120) NOT NULL
);

-- migrate:down

DROP TABLE IF EXISTS career;
