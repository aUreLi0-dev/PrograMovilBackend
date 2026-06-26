-- migrate:up

CREATE TABLE academic_period (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) NOT NULL UNIQUE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_academic_period_dates CHECK (start_date < end_date)
);
CREATE UNIQUE INDEX uq_academic_period_single_active ON academic_period(is_active) WHERE is_active = TRUE;

-- migrate:down

DROP INDEX IF EXISTS uq_academic_period_single_active;
DROP TABLE IF EXISTS academic_period;
