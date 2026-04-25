from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import pandas as pd
import io

from . import models, schemas, crud, analysis
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API d'Analyse des Performances Scolaires")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("templates/index.html", encoding="utf-8") as f:
        return f.read()

@app.get("/api/students", response_model=list[schemas.Student])
def read_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_students(db, skip=skip, limit=limit)

@app.post("/api/students", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    return crud.create_student(db=db, student=student)

@app.delete("/api/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    success = crud.delete_student(db=db, student_id=student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted"}

@app.post("/api/upload-csv")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))
    
    required_cols = ['age', 'gender', 'study_time', 'absences', 'prev_grade', 'final_grade']
    for col in required_cols:
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"Colonne requise manquante : {col}")
    
    students_added = 0
    for _, row in df.iterrows():
        student_data = schemas.StudentCreate(
            age=int(row['age']),
            gender=str(row['gender']),
            study_time=int(row['study_time']),
            absences=int(row['absences']),
            prev_grade=float(row['prev_grade']),
            final_grade=float(row['final_grade'])
        )
        crud.create_student(db, student_data)
        students_added += 1
        
    return {"message": f"{students_added} étudiants importés avec succès"}

@app.get("/api/analysis")
def get_analysis(db: Session = Depends(get_db)):
    students = crud.get_students(db, limit=1000)
    if not students:
        raise HTTPException(status_code=400, detail="Aucune donnée disponible pour l'analyse")
    
    # Convert list of students to DataFrame
    data = [
        {
            "id": s.id,
            "age": s.age,
            "gender": s.gender,
            "study_time": s.study_time,
            "absences": s.absences,
            "prev_grade": s.prev_grade,
            "final_grade": s.final_grade
        }
        for s in students
    ]
    df = pd.DataFrame(data)
    
    result = analysis.run_full_analysis(df)
    return result
