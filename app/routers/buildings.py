from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import BuildingService

router = APIRouter()


@router.get("/buildings")
def get_buildings(db: Session = Depends(get_db)):
    return BuildingService(db).get_buildings()
