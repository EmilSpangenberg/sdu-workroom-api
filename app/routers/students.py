from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import StudentCreate
from app.services import StudentService

router = APIRouter()


@router.post("/students")
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    return StudentService(db).create_student(student)


@router.get("/students")
def get_students(db: Session = Depends(get_db)):
    return StudentService(db).get_students()
