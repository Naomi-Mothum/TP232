from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer)
    gender = Column(String)  # 'M' or 'F'
    study_time = Column(Integer)  # Weekly study time (hours)
    absences = Column(Integer)
    prev_grade = Column(Float)  # Previous period grade
    final_grade = Column(Float) # G3 or Final grade
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User")
