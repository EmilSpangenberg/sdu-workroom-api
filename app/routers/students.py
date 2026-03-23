from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Student
from app.schemas import StudentCreate

router = APIRouter()


@router.post("/students")
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    new_student = Student(sdu_id=student.sdu_id, name=student.name)
    db.add(new_student)
    db.commit()
    return {"message": "Studerende oprettet", "id": new_student.id}


@router.get("/students")
def get_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return [{"id": s.id, "sdu_id": s.sdu_id, "name": s.name} for s in students]
