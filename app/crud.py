from sqlalchemy.orm import Session
from . import models, schemas

def get_students(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Student).filter(models.Student.user_id == user_id).offset(skip).limit(limit).all()

def create_student(db: Session, student: schemas.StudentCreate, user_id: int):
    db_student = models.Student(**student.model_dump(), user_id=user_id)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def delete_student(db: Session, student_id: int, user_id: int):
    db_student = db.query(models.Student).filter(models.Student.id == student_id, models.Student.user_id == user_id).first()
    if db_student:
        db.delete(db_student)
        db.commit()
    return db_student
