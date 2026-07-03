from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text
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
