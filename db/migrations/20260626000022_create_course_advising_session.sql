-- migrate:up

CREATE TABLE course_advising_session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_offering_id INTEGER NOT NULL REFERENCES course_offering(id),
    section_id INTEGER REFERENCES section(id),
    teacher_id INTEGER NOT NULL REFERENCES teacher(id),
    day_of_week INTEGER NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    classroom VARCHAR(100),
    meeting_url VARCHAR(255),
    modality TEXT NOT NULL DEFAULT 'hybrid' CHECK (modality IN ('classroom', 'virtual', 'hybrid')),
    note TEXT,
    CONSTRAINT chk_course_advising_day CHECK (day_of_week BETWEEN 1 AND 7),
    CONSTRAINT chk_course_advising_time CHECK (start_time < end_time)
);
CREATE UNIQUE INDEX uq_course_advising_session_course ON course_advising_session(course_offering_id, teacher_id, day_of_week, start_time) WHERE section_id IS NULL;
CREATE UNIQUE INDEX uq_course_advising_session_section ON course_advising_session(section_id, teacher_id, day_of_week, start_time) WHERE section_id IS NOT NULL;
CREATE INDEX idx_course_advising_session_course_offering ON course_advising_session(course_offering_id);

-- migrate:down

DROP INDEX IF EXISTS idx_course_advising_session_course_offering;
DROP INDEX IF EXISTS uq_course_advising_session_section;
DROP INDEX IF EXISTS uq_course_advising_session_course;
DROP TABLE IF EXISTS course_advising_session;
