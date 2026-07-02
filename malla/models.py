from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

from core.database import ToString

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


class Course(Base, ToString):
    __tablename__ = 'course'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(30), nullable=False, unique=True)
    name = Column(String(150), nullable=False)
    default_credit = Column(Integer, nullable=False)
    origin_faculty = Column(String(120))


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
    courses = relationship('CurriculumCourse', back_populates='curriculum')


class Specialty(Base, ToString):
    __tablename__ = 'specialty'

    id = Column(Integer, primary_key=True, autoincrement=True)
    career_id = Column(Integer, ForeignKey('career.id'), nullable=False)
    name = Column(String(120), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True)


class CurriculumCourse(Base, ToString):
    __tablename__ = 'curriculum_course'

    id = Column(Integer, primary_key=True, autoincrement=True)
    curriculum_id = Column(Integer, ForeignKey('curriculum.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('course.id'), nullable=False)
    cycle = Column(Integer, nullable=False)
    display_order = Column(Integer, nullable=False)
    credit = Column(Integer, nullable=False)
    category = Column(String(30), nullable=False, default='faculty')

    curriculum = relationship('Curriculum', back_populates='courses')
    course = relationship('Course')


class CoursePrerequisite(Base, ToString):
    __tablename__ = 'course_prerequisite'

    id = Column(Integer, primary_key=True, autoincrement=True)
    curriculum_id = Column(Integer, ForeignKey('curriculum.id'), nullable=False)
    curriculum_course_id = Column(Integer, ForeignKey('curriculum_course.id'), nullable=False)
    prerequisite_type = Column(String(30), nullable=False)
    prerequisite_curriculum_course_id = Column(Integer, ForeignKey('curriculum_course.id'))
    required_cycle = Column(Integer)


class CurriculumCourseSpecialty(Base, ToString):
    __tablename__ = 'curriculum_course_specialty'

    curriculum_course_id = Column(Integer, ForeignKey('curriculum_course.id'), primary_key=True)
    specialty_id = Column(Integer, ForeignKey('specialty.id'), primary_key=True)

    specialty = relationship('Specialty')


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


class StudentSpecialty(Base, ToString):
    __tablename__ = 'student_specialty'

    student_id = Column(Integer, ForeignKey('student.id'), primary_key=True)
    specialty_id = Column(Integer, ForeignKey('specialty.id'), primary_key=True)
    selection_type = Column(String(20), nullable=False, default='interest')
    is_active = Column(Boolean, nullable=False, default=True)

    specialty = relationship('Specialty')


class CourseOffering(Base, ToString):
    __tablename__ = 'course_offering'

    id = Column(Integer, primary_key=True, autoincrement=True)
    academic_period_id = Column(Integer, nullable=False)
    course_id = Column(Integer, ForeignKey('course.id'), nullable=False)


class Section(Base, ToString):
    __tablename__ = 'section'

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_offering_id = Column(Integer, ForeignKey('course_offering.id'), nullable=False)
    teacher_id = Column(Integer, nullable=False)
    code = Column(String(30), nullable=False)

    course_offering = relationship('CourseOffering')


class Enrollment(Base, ToString):
    __tablename__ = 'enrollment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    section_id = Column(Integer, ForeignKey('section.id'), nullable=False)
    status = Column(String(30), nullable=False, default='active')

    section = relationship('Section')


class StudentCourseProgress(Base, ToString):
    __tablename__ = 'student_course_progress'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    curriculum_id = Column(Integer, ForeignKey('curriculum.id'), nullable=False)
    curriculum_course_id = Column(Integer, ForeignKey('curriculum_course.id'), nullable=False)
    status = Column(String(30), nullable=False)


class StudentCurriculumSimulation(Base, ToString):
    __tablename__ = 'student_curriculum_simulation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    curriculum_id = Column(Integer, ForeignKey('curriculum.id'), nullable=False)
    curriculum_course_id = Column(Integer, ForeignKey('curriculum_course.id'), nullable=False)
    status = Column(String(30), nullable=False)
