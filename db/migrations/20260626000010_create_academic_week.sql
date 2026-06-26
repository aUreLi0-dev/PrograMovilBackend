-- migrate:up

CREATE TABLE academic_week (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    academic_period_id INTEGER NOT NULL REFERENCES academic_period(id),
    week_number INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    CONSTRAINT uq_academic_week_period_number UNIQUE (academic_period_id, week_number),
    CONSTRAINT chk_academic_week_number CHECK (week_number > 0),
    CONSTRAINT chk_academic_week_dates CHECK (start_date <= end_date)
);

-- migrate:down

DROP TABLE IF EXISTS academic_week;
