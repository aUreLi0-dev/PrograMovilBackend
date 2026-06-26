-- migrate:up

CREATE TABLE curriculum (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    career_id INTEGER NOT NULL UNIQUE REFERENCES career(id),
    name VARCHAR(120) NOT NULL,
    CONSTRAINT uq_curriculum_id_career UNIQUE (id, career_id)
);

-- migrate:down

DROP TABLE IF EXISTS curriculum;
