-- migrate:up

CREATE TABLE curriculum_course (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    curriculum_id INTEGER NOT NULL REFERENCES curriculum(id),
    course_id INTEGER NOT NULL REFERENCES course(id),
    cycle INTEGER NOT NULL,
    display_order INTEGER NOT NULL,
    credit INTEGER NOT NULL,
    category TEXT NOT NULL DEFAULT 'faculty' CHECK (category IN ('general_studies', 'common', 'faculty', 'elective')),
    CONSTRAINT uq_curriculum_course UNIQUE (curriculum_id, course_id),
    CONSTRAINT uq_curriculum_course_id_curriculum UNIQUE (id, curriculum_id),
    CONSTRAINT chk_curriculum_course_cycle CHECK (cycle > 0),
    CONSTRAINT chk_curriculum_course_display_order CHECK (display_order > 0),
    CONSTRAINT chk_curriculum_course_credit CHECK (credit > 0)
);
CREATE INDEX idx_curriculum_course_curriculum ON curriculum_course(curriculum_id);

-- migrate:down

DROP INDEX IF EXISTS idx_curriculum_course_curriculum;
DROP TABLE IF EXISTS curriculum_course;
