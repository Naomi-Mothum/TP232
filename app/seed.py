import random
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models

# Ensure tables are created
models.Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    # Check if already seeded
    if db.query(models.Student).count() > 0:
        print("Base de données déjà initialisée.")
        db.close()
        return

    print("Initialisation de 60 enregistrements d'étudiants...")
    students = []
    for _ in range(60):
        age = random.randint(15, 19)
        gender = random.choice(['M', 'F'])
        study_time = random.randint(1, 15) # Hours per week
        absences = random.randint(0, 20)
        
        # Base grade depends on study time and absences
        base = 7 + (study_time * 0.5) - (absences * 0.2) + random.uniform(-2, 2)
        prev_grade = max(0, min(20, base))
        
        # Final grade depends on prev_grade and more study
        final = prev_grade + (study_time * 0.2) + random.uniform(-1, 1)
        final_grade = max(0, min(20, final))
        
        students.append(models.Student(
            age=age,
            gender=gender,
            study_time=study_time,
            absences=absences,
            prev_grade=round(prev_grade, 1),
            final_grade=round(final_grade, 1)
        ))
    
    db.add_all(students)
    db.commit()
    db.close()
    print("Initialisation terminée.")

if __name__ == "__main__":
    seed_data()
