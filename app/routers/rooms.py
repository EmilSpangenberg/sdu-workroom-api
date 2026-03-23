from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Building, RoomCondition, Workroom
from app.schemas import RoomResponse
from app.utils import haversine_distance

router = APIRouter()


@router.get("/rooms", response_model=List[RoomResponse])
def get_all_rooms(db: Session = Depends(get_db)):
    """
    Hent alle rum.
    db: Session = Depends(get_db) giver automatisk en database session.
    """
    results = []
    rooms = db.query(Workroom).all()

    for room in rooms:
        building = db.query(Building).filter(Building.id == room.building_id).first()
        condition = db.query(RoomCondition).filter(RoomCondition.room_id == room.id).first()

        results.append(RoomResponse(
            id=room.id,
            room_number=room.room_number,
            capacity=room.capacity,
            building_code=building.code if building else "?",
            building_name=building.name if building else "Ukendt",
            is_occupied=condition.is_occupied if condition else False,
            noise_level=condition.noise_level if condition else None,
            temperature=condition.temperature if condition else None,
            latitude=room.latitude,
            longitude=room.longitude
        ))

    return results


@router.get("/rooms/available", response_model=List[RoomResponse])
def get_available_rooms(min_capacity: int = 1, db: Session = Depends(get_db)):
    results = []
    rooms = db.query(Workroom).filter(Workroom.capacity >= min_capacity).all()

    for room in rooms:
        building = db.query(Building).filter(Building.id == room.building_id).first()
        condition = db.query(RoomCondition).filter(RoomCondition.room_id == room.id).first()

        if condition and not condition.is_occupied:
            results.append(RoomResponse(
                id=room.id,
                room_number=room.room_number,
                capacity=room.capacity,
                building_code=building.code if building else "?",
                building_name=building.name if building else "Ukendt",
                is_occupied=False,
                noise_level=condition.noise_level,
                temperature=condition.temperature,
                latitude=room.latitude,
                longitude=room.longitude
            ))

    return results


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
    results = []
    rooms = db.query(Workroom).filter(Workroom.capacity >= min_capacity).all()

    max_distance_meters = max_distance_km * 1000

    for room in rooms:
        building = db.query(Building).filter(Building.id == room.building_id).first()
        condition = db.query(RoomCondition).filter(RoomCondition.room_id == room.id).first()

        if condition and not condition.is_occupied:
            distance = haversine_distance(
                device_latitude,
                device_longitude,
                room.latitude,
                room.longitude
            )

            if distance <= max_distance_meters:
                results.append({
                    "room": RoomResponse(
                        id=room.id,
                        room_number=room.room_number,
                        capacity=room.capacity,
                        building_code=building.code if building else "?",
                        building_name=building.name if building else "Ukendt",
                        is_occupied=False,
                        noise_level=condition.noise_level,
                        temperature=condition.temperature,
                        latitude=room.latitude,
                        longitude=room.longitude,
                        distance_meters=distance
                    ),
                    "distance": distance
                })

    results.sort(key=lambda x: x["distance"])

    return [r["room"] for r in results]
