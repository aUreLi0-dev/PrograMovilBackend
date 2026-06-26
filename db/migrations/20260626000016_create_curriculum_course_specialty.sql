-- migrate:up

CREATE TABLE curriculum_course_specialty (
    curriculum_course_id INTEGER NOT NULL REFERENCES curriculum_course(id),
    specialty_id INTEGER NOT NULL REFERENCES specialty(id),
    PRIMARY KEY (curriculum_course_id, specialty_id)
);

-- migrate:down

DROP TABLE IF EXISTS curriculum_course_specialty;
