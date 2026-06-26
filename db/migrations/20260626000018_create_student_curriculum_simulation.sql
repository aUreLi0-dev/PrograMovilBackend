-- migrate:up

CREATE TABLE student_curriculum_simulation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES student(id),
    curriculum_id INTEGER NOT NULL REFERENCES curriculum(id),
    curriculum_course_id INTEGER NOT NULL REFERENCES curriculum_course(id),
    status TEXT NOT NULL CHECK (status IN ('planned', 'simulated_completed')),
    CONSTRAINT uq_student_curriculum_simulation UNIQUE (student_id, curriculum_course_id)
);
CREATE INDEX idx_student_curriculum_simulation_student ON student_curriculum_simulation(student_id);

-- migrate:down

DROP INDEX IF EXISTS idx_student_curriculum_simulation_student;
DROP TABLE IF EXISTS student_curriculum_simulation;
