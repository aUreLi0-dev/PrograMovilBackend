-- migrate:up

CREATE TABLE section (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_offering_id INTEGER NOT NULL REFERENCES course_offering(id),
    teacher_id INTEGER NOT NULL REFERENCES teacher(id),
    code VARCHAR(30) NOT NULL,
    CONSTRAINT uq_section_offering_code UNIQUE (course_offering_id, code),
    CONSTRAINT uq_section_id_offering UNIQUE (id, course_offering_id)
);
CREATE INDEX idx_section_course_offering ON section(course_offering_id);

-- migrate:down

DROP INDEX IF EXISTS idx_section_course_offering;
DROP TABLE IF EXISTS section;
