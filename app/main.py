from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import pandas as pd
import io

from . import models, schemas, crud, analysis, auth
from .database import engine, get_db
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API d'Analyse des Performances Scolaires")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("templates/index.html", encoding="utf-8") as f:
        return f.read()

@app.post("/api/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/api/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/students", response_model=list[schemas.Student])
def read_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.get_students(db, user_id=current_user.id, skip=skip, limit=limit)

@app.post("/api/students", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.create_student(db=db, student=student, user_id=current_user.id)

@app.delete("/api/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    success = crud.delete_student(db=db, student_id=student_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted"}

@app.post("/api/upload-csv")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
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
        crud.create_student(db, student_data, user_id=current_user.id)
        students_added += 1
        
    return {"message": f"{students_added} étudiants importés avec succès"}

@app.get("/api/analysis")
def get_analysis(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    students = crud.get_students(db, user_id=current_user.id, limit=1000)
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
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
