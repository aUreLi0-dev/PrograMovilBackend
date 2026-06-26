-- migrate:up

CREATE TABLE alert (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES student(id),
    type TEXT NOT NULL CHECK (type IN ('academic_risk', 'high_load')),
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_alert_student ON alert(student_id);

-- migrate:down

DROP INDEX IF EXISTS idx_alert_student;
DROP TABLE IF EXISTS alert;
