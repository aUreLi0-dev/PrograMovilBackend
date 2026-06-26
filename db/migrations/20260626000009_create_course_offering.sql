-- migrate:up

CREATE TABLE course_offering (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    academic_period_id INTEGER NOT NULL REFERENCES academic_period(id),
    course_id INTEGER NOT NULL REFERENCES course(id),
    CONSTRAINT uq_course_offering UNIQUE (academic_period_id, course_id)
);
CREATE INDEX idx_course_offering_period ON course_offering(academic_period_id);

-- migrate:down

DROP INDEX IF EXISTS idx_course_offering_period;
DROP TABLE IF EXISTS course_offering;
