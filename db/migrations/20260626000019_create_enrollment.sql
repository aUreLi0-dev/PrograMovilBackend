-- migrate:up

CREATE TABLE enrollment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES student(id),
    section_id INTEGER NOT NULL REFERENCES section(id),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'withdrawn', 'completed')),
    attended_hours DECIMAL(5, 2) NOT NULL DEFAULT 0,
    absent_hours DECIMAL(5, 2) NOT NULL DEFAULT 0,
    total_hours DECIMAL(5, 2) NOT NULL DEFAULT 0,
    CONSTRAINT uq_enrollment_student_section UNIQUE (student_id, section_id),
    CONSTRAINT uq_enrollment_id_section UNIQUE (id, section_id),
    CONSTRAINT chk_enrollment_attended_hours CHECK (attended_hours >= 0),
    CONSTRAINT chk_enrollment_absent_hours CHECK (absent_hours >= 0),
    CONSTRAINT chk_enrollment_total_hours CHECK (total_hours >= 0),
    CONSTRAINT chk_enrollment_attendance_hours CHECK (attended_hours + absent_hours <= total_hours)
);
CREATE INDEX idx_enrollment_student ON enrollment(student_id);

-- migrate:down

DROP INDEX IF EXISTS idx_enrollment_student;
DROP TABLE IF EXISTS enrollment;
