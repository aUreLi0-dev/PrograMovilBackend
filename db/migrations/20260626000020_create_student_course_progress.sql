-- migrate:up

CREATE TABLE student_course_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES student(id),
    curriculum_id INTEGER NOT NULL REFERENCES curriculum(id),
    curriculum_course_id INTEGER NOT NULL REFERENCES curriculum_course(id),
    status TEXT NOT NULL CHECK (status IN ('in_progress', 'approved', 'failed', 'withdrawn')),
    CONSTRAINT uq_student_course_progress UNIQUE (student_id, curriculum_course_id)
);
CREATE INDEX idx_student_course_progress_student ON student_course_progress(student_id);
CREATE INDEX idx_student_course_progress_curriculum_course ON student_course_progress(curriculum_course_id);

-- migrate:down

DROP INDEX IF EXISTS idx_student_course_progress_curriculum_course;
DROP INDEX IF EXISTS idx_student_course_progress_student;
DROP TABLE IF EXISTS student_course_progress;
