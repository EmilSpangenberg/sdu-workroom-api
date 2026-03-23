from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RoomCondition

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
    condition = db.query(RoomCondition).filter(
        RoomCondition.room_id == room_id
    ).first()

    if not condition:
        raise HTTPException(status_code=404, detail="Rum ikke fundet")

    if noise_level is not None:
        condition.noise_level = noise_level
    if temperature is not None:
        condition.temperature = temperature
    if is_occupied is not None:
        condition.is_occupied = is_occupied

    condition.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Sensor-data opdateret", "room_id": room_id}
