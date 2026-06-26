-- migrate:up

CREATE TABLE student (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE REFERENCES app_user(id),
    career_id INTEGER NOT NULL,
    curriculum_id INTEGER NOT NULL,
    current_level INTEGER,
    specialty_setup_completed BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT uq_student_id_career UNIQUE (id, career_id),
    CONSTRAINT uq_student_id_curriculum UNIQUE (id, curriculum_id),
    CONSTRAINT chk_student_current_level CHECK (current_level IS NULL OR current_level BETWEEN 1 AND 10)
);
CREATE INDEX idx_student_user_id ON student(user_id);
CREATE INDEX idx_student_curriculum_id ON student(curriculum_id);

-- migrate:down

DROP INDEX IF EXISTS idx_student_curriculum_id;
DROP INDEX IF EXISTS idx_student_user_id;
DROP TABLE IF EXISTS student;
