from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from main.database import ToString

Base = declarative_base()

class BodyPart(Base, ToString):
  __tablename__ = 'body_parts'
  id = Column(Integer, primary_key=True, autoincrement=True)
  name = Column(String(10), nullable=False)


class Exercise(Base, ToString):
  __tablename__ = 'exercises'
  id = Column(Integer, primary_key=True, autoincrement=True)
  name = Column(String(40), nullable=False)
  image_url = Column(String(40))
  body_part_id = Column(Integer, ForeignKey('body_parts.id'), nullable=False)

  body_part = relationship('BodyPart')

class Member(Base, ToString):
    __tablename__ = 'members'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(40))
    codigo = Column(String(5))
    dni = Column(String(8))
    email = Column(String(40))
    phone = Column(String(40))

    # Relación con la tabla 'users', si deseas acceder a los usuarios asociados a un miembro
    users = relationship("User", back_populates="member")

class User(Base, ToString):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(20))
    password = Column(String(250))
    member_id = Column(Integer, ForeignKey('members.id'))

    # Definir la relación con la tabla 'members' (suponiendo que tienes una tabla `members` con una columna 'id')
    member = relationship("Member", back_populates="users")