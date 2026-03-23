from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Building

router = APIRouter()


@router.get("/buildings")
def get_buildings(db: Session = Depends(get_db)):
    buildings = db.query(Building).all()
    return [{"id": b.id, "name": b.name, "code": b.code} for b in buildings]
