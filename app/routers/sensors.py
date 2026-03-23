from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import SensorService

router = APIRouter()


@router.post("/sensors/update")
def update_sensor_data(
    room_id: int,
    noise_level: Optional[float] = None,
    temperature: Optional[float] = None,
    is_occupied: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Opdater sensor data.
    Mange sensorer kan opdatere samtidig - det er OK.
    """
    return SensorService(db).update_sensor_data(
        room_id=room_id,
        noise_level=noise_level,
        temperature=temperature,
        is_occupied=is_occupied,
    )
