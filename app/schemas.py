from pydantic import BaseModel
from typing import List, Optional

class StudentBase(BaseModel):
    age: int
    gender: str
    study_time: int
    absences: int
    prev_grade: float
    final_grade: float

class StudentCreate(StudentBase):
    pass

class Student(StudentBase):
    id: int

    class Config:
        from_attributes = True

class AnalysisResult(BaseModel):
    simple_regression: dict
    multiple_regression: dict
    pca_data: List[dict]
    clusters: List[dict]
    pass_fail_prediction: dict
