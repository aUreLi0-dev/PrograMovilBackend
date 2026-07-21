-- migrate:up

DROP INDEX IF EXISTS idx_student_curriculum_simulation_student;
ALTER TABLE student_curriculum_simulation RENAME TO student_curriculum_simulation_old;

CREATE TABLE student_curriculum_simulation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES student(id),
    curriculum_id INTEGER NOT NULL REFERENCES curriculum(id),
    curriculum_course_id INTEGER NOT NULL REFERENCES curriculum_course(id),
    status TEXT NOT NULL CHECK (status IN ('simulated_in_progress', 'simulated_approved', 'simulated_unlocked', 'simulated_locked')),
    CONSTRAINT uq_student_curriculum_simulation UNIQUE (student_id, curriculum_course_id)
);

INSERT INTO student_curriculum_simulation (id, student_id, curriculum_id, curriculum_course_id, status)
SELECT id, student_id, curriculum_id, curriculum_course_id, status
FROM student_curriculum_simulation_old;

DROP TABLE student_curriculum_simulation_old;
CREATE INDEX idx_student_curriculum_simulation_student ON student_curriculum_simulation(student_id);

-- migrate:down

DROP INDEX IF EXISTS idx_student_curriculum_simulation_student;
DELETE FROM student_curriculum_simulation
WHERE status NOT IN ('simulated_in_progress', 'simulated_approved');
ALTER TABLE student_curriculum_simulation RENAME TO student_curriculum_simulation_old;

CREATE TABLE student_curriculum_simulation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES student(id),
    curriculum_id INTEGER NOT NULL REFERENCES curriculum(id),
    curriculum_course_id INTEGER NOT NULL REFERENCES curriculum_course(id),
    status TEXT NOT NULL CHECK (status IN ('simulated_in_progress', 'simulated_approved')),
    CONSTRAINT uq_student_curriculum_simulation UNIQUE (student_id, curriculum_course_id)
);

INSERT INTO student_curriculum_simulation (id, student_id, curriculum_id, curriculum_course_id, status)
SELECT id, student_id, curriculum_id, curriculum_course_id, status
FROM student_curriculum_simulation_old;

DROP TABLE student_curriculum_simulation_old;
CREATE INDEX idx_student_curriculum_simulation_student ON student_curriculum_simulation(student_id);
