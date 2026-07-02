from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean, DECIMAL, Text, Time
from sqlalchemy.orm import declarative_base, relationship
from core.database import ToString, engine

Base = declarative_base()

class AssessmentType(Base, ToString):
    __tablename__ = 'assessment_type'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False, unique=True)
    abbreviation = Column(String(30))
    description = Column(Text)

class Course(Base, ToString):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(30), nullable=False, unique=True)
    name = Column(String(150), nullable=False)
    default_credit = Column(Integer, nullable=False)
    origin_faculty = Column(String(120))

class AcademicPeriod(Base, ToString):
    __tablename__ = 'academic_period'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), nullable=False, unique=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

class CourseOffering(Base, ToString):
    __tablename__ = 'course_offering'
    id = Column(Integer, primary_key=True, autoincrement=True)
    academic_period_id = Column(Integer, ForeignKey('academic_period.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('course.id'), nullable=False)
    academic_period = relationship('AcademicPeriod')
    course = relationship('Course')

class Syllabus(Base, ToString):
    __tablename__ = 'syllabus'
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_offering_id = Column(Integer, ForeignKey('course_offering.id'), nullable=False, unique=True)
    title = Column(String(150))
    drive_file_id = Column(String(120), nullable=False, unique=True)
    drive_file_url = Column(String(255), nullable=False)
    course_offering = relationship('CourseOffering')

class Teacher(Base, ToString):
    __tablename__ = 'teacher'
    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_code = Column(String(50), unique=True)
    full_name = Column(String(150), nullable=False)
    institutional_email = Column(String(150), unique=True)

class Section(Base, ToString):
    __tablename__ = 'section'
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_offering_id = Column(Integer, ForeignKey('course_offering.id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('teacher.id'), nullable=False)
    code = Column(String(30), nullable=False)
    course_offering = relationship('CourseOffering')
    teacher = relationship('Teacher')

class AppUser(Base, ToString):
    __tablename__ = 'app_user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(30), nullable=False, unique=True)
    full_name = Column(String(150), nullable=False)
    institutional_email = Column(String(150), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    google_id = Column(String(255))
    token_version = Column(Integer, nullable=False, default=1)

class Career(Base, ToString):
    __tablename__ = 'career'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(30), nullable=False, unique=True)
    name = Column(String(120), nullable=False)
    faculty = Column(String(120), nullable=False)

class Curriculum(Base, ToString):
    __tablename__ = 'curriculum'
    id = Column(Integer, primary_key=True, autoincrement=True)
    career_id = Column(Integer, ForeignKey('career.id'), nullable=False, unique=True)
    name = Column(String(120), nullable=False)
    career = relationship('Career')

class Student(Base, ToString):
    __tablename__ = 'student'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('app_user.id'), nullable=False, unique=True)
    career_id = Column(Integer, ForeignKey('career.id'), nullable=False)
    curriculum_id = Column(Integer, ForeignKey('curriculum.id'), nullable=False)
    current_level = Column(Integer)
    specialty_setup_completed = Column(Boolean, nullable=False, default=False)
    user = relationship('AppUser')
    career = relationship('Career')
    curriculum = relationship('Curriculum')
    enrollments = relationship('Enrollment', back_populates='student')

class Enrollment(Base, ToString):
    __tablename__ = 'enrollment'
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    section_id = Column(Integer, ForeignKey('section.id'), nullable=False)
    status = Column(String(30), nullable=False, default='active')
    attended_hours = Column(DECIMAL(5, 2), nullable=False, default=0)
    absent_hours = Column(DECIMAL(5, 2), nullable=False, default=0)
    total_hours = Column(DECIMAL(5, 2), nullable=False, default=0)
    student = relationship('Student', back_populates='enrollments')
    section = relationship('Section')
    scores = relationship('StudentScore', back_populates='enrollment')

class Assessment(Base, ToString):
    __tablename__ = 'assessment'
    id = Column(Integer, primary_key=True, autoincrement=True)
    syllabus_id = Column(Integer, ForeignKey('syllabus.id'), nullable=False)
    assessment_type_id = Column(Integer, ForeignKey('assessment_type.id'), nullable=False)
    code = Column(String(30), nullable=False)
    name = Column(String(150), nullable=False)
    week_number = Column(Integer, nullable=False)
    weight = Column(DECIMAL(5, 2), nullable=False)
    syllabus = relationship('Syllabus')
    assessment_type = relationship('AssessmentType')

class StudentScore(Base, ToString):
    __tablename__ = 'student_score'
    id = Column(Integer, primary_key=True, autoincrement=True)
    enrollment_id = Column(Integer, ForeignKey('enrollment.id'), nullable=False)
    assessment_id = Column(Integer, ForeignKey('assessment.id'), nullable=False)
    value = Column(DECIMAL(5, 2))
    enrollment = relationship('Enrollment', back_populates='scores')
    assessment = relationship('Assessment')

class Specialty(Base, ToString):
    __tablename__ = 'specialty'
    id = Column(Integer, primary_key=True, autoincrement=True)
    career_id = Column(Integer, ForeignKey('career.id'), nullable=False)
    name = Column(String(120), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True)
    career = relationship('Career')

class StudentSpecialty(Base, ToString):
    __tablename__ = 'student_specialty'
    student_id = Column(Integer, ForeignKey('student.id'), primary_key=True)
    specialty_id = Column(Integer, ForeignKey('specialty.id'), primary_key=True)
    selection_type = Column(String(20), nullable=False, default='interest')
    is_active = Column(Boolean, nullable=False, default=True)
    student = relationship('Student')
    specialty = relationship('Specialty')

class ScheduleSession(Base, ToString):
    __tablename__ = 'schedule_session'
    id = Column(Integer, primary_key=True, autoincrement=True)
    section_id = Column(Integer, ForeignKey('section.id'), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    classroom = Column(String(100))
    color_hex = Column(String(20))

    section = relationship('Section')

class CourseAdvisingSession(Base, ToString):
    __tablename__ = 'course_advising_session'
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_offering_id = Column(Integer, ForeignKey('course_offering.id'), nullable=False)
    section_id = Column(Integer, ForeignKey('section.id'))
    teacher_id = Column(Integer, ForeignKey('teacher.id'), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    classroom = Column(String(100))
    meeting_url = Column(String(255))
    modality = Column(String(50), nullable=False, default='hybrid')
    note = Column(Text)

    course_offering = relationship('CourseOffering')
    section = relationship('Section')
    teacher = relationship('Teacher')
