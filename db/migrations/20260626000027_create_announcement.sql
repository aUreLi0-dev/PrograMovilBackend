-- migrate:up

CREATE TABLE announcement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_representative_id INTEGER NOT NULL REFERENCES section_representative(id),
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    published_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- migrate:down

DROP TABLE IF EXISTS announcement;
