from pydantic import BaseModel
from typing import List, Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True


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
