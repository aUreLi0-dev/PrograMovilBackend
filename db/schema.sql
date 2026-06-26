CREATE TABLE IF NOT EXISTS "schema_migrations" (version varchar(128) primary key);
-- ==========================================
-- 1. TABLAS SIN DEPENDENCIAS (Base)
-- ==========================================
CREATE TABLE app_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(30) NOT NULL UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    institutional_email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    google_id VARCHAR(255),
    token_version INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE career (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(120) NOT NULL,
    faculty VARCHAR(120) NOT NULL
);

CREATE TABLE teacher (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_code VARCHAR(50) UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    institutional_email VARCHAR(150) UNIQUE
);

CREATE TABLE course (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    default_credit INTEGER NOT NULL,
    origin_faculty VARCHAR(120),
    CONSTRAINT chk_course_default_credit CHECK (default_credit &gt; 0)
);

CREATE TABLE academic_period (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) NOT NULL UNIQUE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_academic_period_dates CHECK (start_date &lt; end_date)
);
CREATE UNIQUE INDEX uq_academic_period_single_active ON academic_period(is_active) WHERE is_active = TRUE;

CREATE TABLE assessment_type (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(120) NOT NULL UNIQUE,
    abbreviation VARCHAR(30),
    description TEXT
);

-- ==========================================
-- 2. TABLAS DE PRIMER NIVEL DE DEPENDENCIA
-- ==========================================
CREATE TABLE curriculum (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    career_id INTEGER NOT NULL UNIQUE REFERENCES career(id),
    name VARCHAR(120) NOT NULL,
    CONSTRAINT uq_curriculum_id_career UNIQUE (id, career_id)
);

CREATE TABLE specialty (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    career_id INTEGER NOT NULL REFERENCES career(id),
    name VARCHAR(120) NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_specialty_career_name UNIQUE (career_id, name)
);

CREATE TABLE course_offering (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    academic_period_id INTEGER NOT NULL REFERENCES academic_period(id),
    course_id INTEGER NOT NULL REFERENCES course(id),
    CONSTRAINT uq_course_offering UNIQUE (academic_period_id, course_id)
);
CREATE INDEX idx_course_offering_period ON course_offering(academic_period_id);

CREATE TABLE academic_week (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    academic_period_id INTEGER NOT NULL REFERENCES academic_period(id),
    week_number INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    CONSTRAINT uq_academic_week_period_number UNIQUE (academic_period_id, week_number),
    CONSTRAINT chk_academic_week_number CHECK (week_number &gt; 0),
    CONSTRAINT chk_academic_week_dates CHECK (start_date &lt;= end_date)
);

-- ==========================================
-- 3. TABLAS DE SEGUNDO NIVEL DE DEPENDENCIA
-- ==========================================
CREATE TABLE student (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE REFERENCES app_user(id),
    career_id INTEGER NOT NULL,
    curriculum_id INTEGER NOT NULL,
    current_level INTEGER,
    specialty_setup_completed BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT uq_student_id_career UNIQUE (id, career_id),
    CONSTRAINT uq_student_id_curriculum UNIQUE (id, curriculum_id),
    CONSTRAINT chk_student_current_level CHECK (current_level IS NULL OR current_level BETWEEN 1 AND 10)
);
CREATE INDEX idx_student_user_id ON student(user_id);
CREATE INDEX idx_student_curriculum_id ON student(curriculum_id);

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
    CONSTRAINT chk_curriculum_course_cycle CHECK (cycle &gt; 0),
    CONSTRAINT chk_curriculum_course_display_order CHECK (display_order &gt; 0),
    CONSTRAINT chk_curriculum_course_credit CHECK (credit &gt; 0)
);
CREATE INDEX idx_curriculum_course_curriculum ON curriculum_course(curriculum_id);

CREATE TABLE syllabus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_offering_id INTEGER NOT NULL UNIQUE REFERENCES course_offering(id),
    title VARCHAR(150),
    drive_file_id VARCHAR(120) NOT NULL UNIQUE,
    drive_file_url VARCHAR(255) NOT NULL
);

CREATE TABLE section (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_offering_id INTEGER NOT NULL REFERENCES course_offering(id),
    teacher_id INTEGER NOT NULL REFERENCES teacher(id),
    code VARCHAR(30) NOT NULL,
    CONSTRAINT uq_section_offering_code UNIQUE (course_offering_id, code),
    CONSTRAINT uq_section_id_offering UNIQUE (id, course_offering_id)
);
CREATE INDEX idx_section_course_offering ON section(course_offering_id);

-- ==========================================
-- 4. TABLAS DE TERCER NIVEL Y SUPERIOR
-- ==========================================
CREATE TABLE student_specialty (
    student_id INTEGER NOT NULL REFERENCES student(id),
    specialty_id INTEGER NOT NULL REFERENCES specialty(id),
    selection_type TEXT NOT NULL DEFAULT 'interest' CHECK (selection_type IN ('primary', 'interest')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (student_id, specialty_id)
);
CREATE INDEX idx_student_specialty_student ON student_specialty(student_id);
CREATE UNIQUE INDEX uq_student_specialty_active_primary ON student_specialty(student_id) WHERE selection_type = 'primary' AND is_active = TRUE;

CREATE TABLE curriculum_course_specialty (
    curriculum_course_id INTEGER NOT NULL REFERENCES curriculum_course(id),
    specialty_id INTEGER NOT NULL REFERENCES specialty(id),
    PRIMARY KEY (curriculum_course_id, specialty_id)
);

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
    CONSTRAINT chk_course_prerequisite_required_cycle CHECK (required_cycle IS NULL OR required_cycle &gt; 0),
    CONSTRAINT chk_course_prerequisite_not_self CHECK (prerequisite_curriculum_course_id IS NULL OR curriculum_course_id &lt;&gt; prerequisite_curriculum_course_id)
);
CREATE UNIQUE INDEX uq_course_prerequisite_course ON course_prerequisite(curriculum_course_id, prerequisite_curriculum_course_id) WHERE prerequisite_curriculum_course_id IS NOT NULL;
CREATE UNIQUE INDEX uq_course_prerequisite_completed_cycle ON course_prerequisite(curriculum_course_id, prerequisite_type, required_cycle) WHERE required_cycle IS NOT NULL;
CREATE INDEX idx_course_prerequisite_curriculum_course ON course_prerequisite(curriculum_course_id);

CREATE TABLE student_curriculum_simulation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES student(id),
    curriculum_id INTEGER NOT NULL REFERENCES curriculum(id),
    curriculum_course_id INTEGER NOT NULL REFERENCES curriculum_course(id),
    status TEXT NOT NULL CHECK (status IN ('planned', 'simulated_completed')),
    CONSTRAINT uq_student_curriculum_simulation UNIQUE (student_id, curriculum_course_id)
);
CREATE INDEX idx_student_curriculum_simulation_student ON student_curriculum_simulation(student_id);

CREATE TABLE enrollment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES student(id),
    section_id INTEGER NOT NULL REFERENCES section(id),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'withdrawn', 'completed')),
    attended_hours DECIMAL(5, 2) NOT NULL DEFAULT 0,
    absent_hours DECIMAL(5, 2) NOT NULL DEFAULT 0,
    total_hours DECIMAL(5, 2) NOT NULL DEFAULT 0,
    CONSTRAINT uq_enrollment_student_section UNIQUE (student_id, section_id),
    CONSTRAINT uq_enrollment_id_section UNIQUE (id, section_id),
    CONSTRAINT chk_enrollment_attended_hours CHECK (attended_hours &gt;= 0),
    CONSTRAINT chk_enrollment_absent_hours CHECK (absent_hours &gt;= 0),
    CONSTRAINT chk_enrollment_total_hours CHECK (total_hours &gt;= 0),
    CONSTRAINT chk_enrollment_attendance_hours CHECK (attended_hours + absent_hours &lt;= total_hours)
);
CREATE INDEX idx_enrollment_student ON enrollment(student_id);

CREATE TABLE student_course_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES student(id),
    curriculum_id INTEGER NOT NULL REFERENCES curriculum(id),
    curriculum_course_id INTEGER NOT NULL REFERENCES curriculum_course(id),
    status TEXT NOT NULL CHECK (status IN ('in_progress', 'approved', 'failed', 'withdrawn')),
    CONSTRAINT uq_student_course_progress UNIQUE (student_id, curriculum_course_id)
);
CREATE INDEX idx_student_course_progress_student ON student_course_progress(student_id);
CREATE INDEX idx_student_course_progress_curriculum_course ON student_course_progress(curriculum_course_id);

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
    CONSTRAINT chk_schedule_session_time CHECK (start_time &lt; end_time)
);
CREATE INDEX idx_schedule_session_section ON schedule_session(section_id);

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
    CONSTRAINT chk_course_advising_time CHECK (start_time &lt; end_time)
);
CREATE UNIQUE INDEX uq_course_advising_session_course ON course_advising_session(course_offering_id, teacher_id, day_of_week, start_time) WHERE section_id IS NULL;
CREATE UNIQUE INDEX uq_course_advising_session_section ON course_advising_session(section_id, teacher_id, day_of_week, start_time) WHERE section_id IS NOT NULL;
CREATE INDEX idx_course_advising_session_course_offering ON course_advising_session(course_offering_id);

CREATE TABLE assessment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    syllabus_id INTEGER NOT NULL REFERENCES syllabus(id),
    assessment_type_id INTEGER NOT NULL REFERENCES assessment_type(id),
    code VARCHAR(30) NOT NULL,
    name VARCHAR(150) NOT NULL,
    week_number INTEGER NOT NULL,
    weight DECIMAL(5, 2) NOT NULL,
    CONSTRAINT uq_assessment_syllabus_code UNIQUE (syllabus_id, code),
    CONSTRAINT chk_assessment_week_number CHECK (week_number &gt; 0),
    CONSTRAINT chk_assessment_weight CHECK (weight &gt; 0 AND weight &lt;= 100)
);
CREATE INDEX idx_assessment_syllabus ON assessment(syllabus_id);

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

-- ==========================================
-- 5. TABLAS DE CUARTO NIVEL Y SUPERIOR
-- ==========================================
CREATE TABLE section_representative (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id INTEGER NOT NULL REFERENCES section(id),
    enrollment_id INTEGER NOT NULL UNIQUE REFERENCES enrollment(id),
    position TEXT NOT NULL CHECK (position IN ('delegate', 'subdelegate')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE UNIQUE INDEX uq_active_section_representative_position ON section_representative(section_id, position) WHERE is_active = TRUE;

CREATE TABLE student_score (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL REFERENCES enrollment(id),
    assessment_id INTEGER NOT NULL REFERENCES assessment(id),
    value DECIMAL(5, 2),
    CONSTRAINT uq_student_score UNIQUE (enrollment_id, assessment_id),
    CONSTRAINT chk_student_score_value CHECK (value IS NULL OR value BETWEEN 0 AND 20)
);
CREATE INDEX idx_student_score_enrollment ON student_score(enrollment_id);

CREATE TABLE announcement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_representative_id INTEGER NOT NULL REFERENCES section_representative(id),
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    published_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);
-- Dbmate schema migrations
INSERT INTO "schema_migrations" (version) VALUES
  ('20260626000001'),
  ('20260626000002'),
  ('20260626000003'),
  ('20260626000004'),
  ('20260626000005'),
  ('20260626000006'),
  ('20260626000007'),
  ('20260626000008'),
  ('20260626000009'),
  ('20260626000010'),
  ('20260626000011'),
  ('20260626000012'),
  ('20260626000013'),
  ('20260626000014'),
  ('20260626000015'),
  ('20260626000016'),
  ('20260626000017'),
  ('20260626000018'),
  ('20260626000019'),
  ('20260626000020'),
  ('20260626000021'),
  ('20260626000022'),
  ('20260626000023'),
  ('20260626000024'),
  ('20260626000025'),
  ('20260626000026'),
  ('20260626000027');
