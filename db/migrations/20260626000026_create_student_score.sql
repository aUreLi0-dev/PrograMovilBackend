-- migrate:up

CREATE TABLE student_score (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL REFERENCES enrollment(id),
    assessment_id INTEGER NOT NULL REFERENCES assessment(id),
    value DECIMAL(5, 2),
    CONSTRAINT uq_student_score UNIQUE (enrollment_id, assessment_id),
    CONSTRAINT chk_student_score_value CHECK (value IS NULL OR value BETWEEN 0 AND 20)
);
CREATE INDEX idx_student_score_enrollment ON student_score(enrollment_id);

-- migrate:down

DROP INDEX IF EXISTS idx_student_score_enrollment;
DROP TABLE IF EXISTS student_score;
