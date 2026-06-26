-- migrate:up

CREATE TABLE specialty (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    career_id INTEGER NOT NULL REFERENCES career(id),
    name VARCHAR(120) NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_specialty_career_name UNIQUE (career_id, name)
);

-- migrate:down

DROP TABLE IF EXISTS specialty;
