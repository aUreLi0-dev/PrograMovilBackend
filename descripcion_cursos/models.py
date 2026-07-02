from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    DECIMAL,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.orm import declarative_base, relationship

from main.database import ToString

Base = declarative_base()


class AppUser(Base, ToString):
    __tablename__ = 'app_user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(30), nullable=False, unique=True)
    full_name = Column(String(150), nullable=False)
    institutional_email = Column(String(150), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    google_id = Column(String(255))
    token_version = Column(Integer, nullable=False, default=1)


class Teacher(Base, ToString):
    __tablename__ = 'teacher'

    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_code = Column(String(50), unique=True)
    full_name = Column(String(150), nullable=False)
    institutional_email = Column(String(150), unique=True)


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


class Section(Base, ToString):
    __tablename__ = 'section'

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_offering_id = Column(Integer, ForeignKey('course_offering.id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('teacher.id'), nullable=False)
    code = Column(String(30), nullable=False)

    course_offering = relationship('CourseOffering')
    teacher = relationship('Teacher')
    enrollments = relationship('Enrollment', back_populates='section')
    schedule_sessions = relationship('ScheduleSession', back_populates='section')
    representatives = relationship('SectionRepresentative', back_populates='section')


class Student(Base, ToString):
    __tablename__ = 'student'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('app_user.id'), nullable=False, unique=True)
    career_id = Column(Integer, nullable=False)
    curriculum_id = Column(Integer, nullable=False)
    current_level = Column(Integer)
    specialty_setup_completed = Column(Boolean, nullable=False, default=False)

    user = relationship('AppUser')
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
    section = relationship('Section', back_populates='enrollments')
    scores = relationship('StudentScore', back_populates='enrollment')
    representatives = relationship('SectionRepresentative', back_populates='enrollment')


class Assessment(Base, ToString):
    __tablename__ = 'assessment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    syllabus_id = Column(Integer, ForeignKey('syllabus.id'), nullable=False)
    assessment_type_id = Column(Integer, nullable=False)
    code = Column(String(30), nullable=False)
    name = Column(String(150), nullable=False)
    week_number = Column(Integer, nullable=False)
    weight = Column(DECIMAL(5, 2), nullable=False)

    syllabus = relationship('Syllabus')
    scores = relationship('StudentScore', back_populates='assessment')


class StudentScore(Base, ToString):
    __tablename__ = 'student_score'

    id = Column(Integer, primary_key=True, autoincrement=True)
    enrollment_id = Column(Integer, ForeignKey('enrollment.id'), nullable=False)
    assessment_id = Column(Integer, ForeignKey('assessment.id'), nullable=False)
    value = Column(DECIMAL(5, 2))

    enrollment = relationship('Enrollment', back_populates='scores')
    assessment = relationship('Assessment', back_populates='scores')


class ScheduleSession(Base, ToString):
    __tablename__ = 'schedule_session'

    id = Column(Integer, primary_key=True, autoincrement=True)
    section_id = Column(Integer, ForeignKey('section.id'), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    classroom = Column(String(100))
    color_hex = Column(String(20))

    section = relationship('Section', back_populates='schedule_sessions')


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
    modality = Column(Text, nullable=False, default='hybrid')
    note = Column(Text)

    course_offering = relationship('CourseOffering')
    section = relationship('Section')
    teacher = relationship('Teacher')


class SectionRepresentative(Base, ToString):
    __tablename__ = 'section_representative'

    id = Column(Integer, primary_key=True, autoincrement=True)
    section_id = Column(Integer, ForeignKey('section.id'), nullable=False)
    enrollment_id = Column(Integer, ForeignKey('enrollment.id'), nullable=False, unique=True)
    position = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    section = relationship('Section', back_populates='representatives')
    enrollment = relationship('Enrollment', back_populates='representatives')
    announcements = relationship('Announcement', back_populates='section_representative')


class Announcement(Base, ToString):
    __tablename__ = 'announcement'

    id = Column(Integer, primary_key=True, autoincrement=True)
    section_representative_id = Column(Integer, ForeignKey('section_representative.id'), nullable=False)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    published_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    section_representative = relationship('SectionRepresentative', back_populates='announcements')
