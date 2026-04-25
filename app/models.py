from sqlalchemy import Column, Integer, String, Float
from .database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer)
    gender = Column(String)  # 'M' or 'F'
    study_time = Column(Integer)  # Weekly study time (hours)
    absences = Column(Integer)
    prev_grade = Column(Float)  # Previous period grade
    final_grade = Column(Float) # G3 or Final grade
