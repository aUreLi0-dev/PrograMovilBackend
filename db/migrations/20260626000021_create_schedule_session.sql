-- migrate:up

CREATE TABLE schedule_session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id INTEGER NOT NULL REFERENCES section(id),
    day_of_week INTEGER NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    classroom VARCHAR(100),
    color_hex VARCHAR(20),
    CONSTRAINT uq_schedule_session UNIQUE (section_id, day_of_week, start_time),
    CONSTRAINT chk_schedule_session_day CHECK (day_of_week BETWEEN 1 AND 7),
    CONSTRAINT chk_schedule_session_time CHECK (start_time < end_time)
);
CREATE INDEX idx_schedule_session_section ON schedule_session(section_id);

-- migrate:down

DROP INDEX IF EXISTS idx_schedule_session_section;
DROP TABLE IF EXISTS schedule_session;
