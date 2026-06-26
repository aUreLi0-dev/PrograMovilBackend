-- migrate:up

CREATE TABLE course_prerequisite (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    curriculum_id INTEGER NOT NULL REFERENCES curriculum(id),
    curriculum_course_id INTEGER NOT NULL REFERENCES curriculum_course(id),
    prerequisite_type TEXT NOT NULL CHECK (prerequisite_type IN ('course', 'completed_cycle')),
    prerequisite_curriculum_course_id INTEGER REFERENCES curriculum_course(id),
    required_cycle INTEGER,
    CONSTRAINT chk_course_prerequisite_kind CHECK (
        (prerequisite_type = 'course' AND prerequisite_curriculum_course_id IS NOT NULL AND required_cycle IS NULL)
        OR
        (prerequisite_type = 'completed_cycle' AND prerequisite_curriculum_course_id IS NULL AND required_cycle IS NOT NULL)
    ),
    CONSTRAINT chk_course_prerequisite_required_cycle CHECK (required_cycle IS NULL OR required_cycle > 0),
    CONSTRAINT chk_course_prerequisite_not_self CHECK (prerequisite_curriculum_course_id IS NULL OR curriculum_course_id <> prerequisite_curriculum_course_id)
);
CREATE UNIQUE INDEX uq_course_prerequisite_course ON course_prerequisite(curriculum_course_id, prerequisite_curriculum_course_id) WHERE prerequisite_curriculum_course_id IS NOT NULL;
CREATE UNIQUE INDEX uq_course_prerequisite_completed_cycle ON course_prerequisite(curriculum_course_id, prerequisite_type, required_cycle) WHERE required_cycle IS NOT NULL;
CREATE INDEX idx_course_prerequisite_curriculum_course ON course_prerequisite(curriculum_course_id);

-- migrate:down

DROP INDEX IF EXISTS idx_course_prerequisite_curriculum_course;
DROP INDEX IF EXISTS uq_course_prerequisite_completed_cycle;
DROP INDEX IF EXISTS uq_course_prerequisite_course;
DROP TABLE IF EXISTS course_prerequisite;
