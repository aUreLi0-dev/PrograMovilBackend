-- migrate:up

CREATE TABLE student_specialty (
    student_id INTEGER NOT NULL REFERENCES student(id),
    specialty_id INTEGER NOT NULL REFERENCES specialty(id),
    selection_type TEXT NOT NULL DEFAULT 'interest' CHECK (selection_type IN ('primary', 'interest')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (student_id, specialty_id)
);
CREATE INDEX idx_student_specialty_student ON student_specialty(student_id);
CREATE UNIQUE INDEX uq_student_specialty_active_primary ON student_specialty(student_id) WHERE selection_type = 'primary' AND is_active = TRUE;

-- migrate:down

DROP INDEX IF EXISTS uq_student_specialty_active_primary;
DROP INDEX IF EXISTS idx_student_specialty_student;
DROP TABLE IF EXISTS student_specialty;
