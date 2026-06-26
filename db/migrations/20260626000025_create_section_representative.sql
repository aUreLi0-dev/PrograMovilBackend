-- migrate:up

CREATE TABLE section_representative (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id INTEGER NOT NULL REFERENCES section(id),
    enrollment_id INTEGER NOT NULL UNIQUE REFERENCES enrollment(id),
    position TEXT NOT NULL CHECK (position IN ('delegate', 'subdelegate')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE UNIQUE INDEX uq_active_section_representative_position ON section_representative(section_id, position) WHERE is_active = TRUE;

-- migrate:down

DROP INDEX IF EXISTS uq_active_section_representative_position;
DROP TABLE IF EXISTS section_representative;
