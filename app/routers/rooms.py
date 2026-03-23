from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import RoomResponse
from app.services import RoomService

router = APIRouter()


@router.get("/rooms", response_model=List[RoomResponse])
def get_all_rooms(db: Session = Depends(get_db)):
    """
    Hent alle rum.
    db: Session = Depends(get_db) giver automatisk en database session.
    """
    return RoomService(db).get_all_rooms()


@router.get("/rooms/available", response_model=List[RoomResponse])
def get_available_rooms(min_capacity: int = 1, db: Session = Depends(get_db)):
    return RoomService(db).get_available_rooms(min_capacity)


@router.get("/rooms/nearest", response_model=List[RoomResponse])
def get_nearest_available_rooms(
    device_latitude: float,
    device_longitude: float,
    min_capacity: int = 1,
    max_distance_km: float = 10.0,
    db: Session = Depends(get_db)
):
    """
    Find nearest available rooms based on device GPS coordinates.

    Query Parameters:
    - device_latitude: Device's current latitude
    - device_longitude: Device's current longitude
    - min_capacity: Minimum room capacity required (default: 1)
    - max_distance_km: Maximum search radius in kilometers (default: 10 km)

    Returns: Available rooms sorted by distance (nearest first)
    """
    return RoomService(db).get_nearest_available_rooms(
        device_latitude=device_latitude,
        device_longitude=device_longitude,
        min_capacity=min_capacity,
        max_distance_km=max_distance_km,
    )
