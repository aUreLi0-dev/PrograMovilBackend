-- migrate:up

CREATE TABLE assessment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    syllabus_id INTEGER NOT NULL REFERENCES syllabus(id),
    assessment_type_id INTEGER NOT NULL REFERENCES assessment_type(id),
    code VARCHAR(30) NOT NULL,
    name VARCHAR(150) NOT NULL,
    week_number INTEGER NOT NULL,
    weight DECIMAL(5, 2) NOT NULL,
    CONSTRAINT uq_assessment_syllabus_code UNIQUE (syllabus_id, code),
    CONSTRAINT chk_assessment_week_number CHECK (week_number > 0),
    CONSTRAINT chk_assessment_weight CHECK (weight > 0 AND weight <= 100)
);
CREATE INDEX idx_assessment_syllabus ON assessment(syllabus_id);

-- migrate:down

DROP INDEX IF EXISTS idx_assessment_syllabus;
DROP TABLE IF EXISTS assessment;
