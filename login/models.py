from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from core.database import ToString

Base = declarative_base()

class User(Base, ToString):
    __tablename__ = 'app_user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(30), nullable=False, unique=True)
    full_name = Column(String(150), nullable=False)
    institutional_email = Column(String(150), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    google_id = Column(String(255))
    token_version = Column(Integer, nullable=False, default=1)