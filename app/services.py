from datetime import datetime
from typing import List, Optional, Tuple

from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models import Booking, Building, RoomCondition, Student, Workroom
from app.schemas import BookingCreate, BookingNearestCreate, BookingResponse, RoomResponse, StudentCreate
from app.utils import haversine_distance


class RoomService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_room_response(
        room: Workroom,
        building: Optional[Building],
        condition: Optional[RoomCondition],
        distance_meters: Optional[float] = None,
        force_available: bool = False,
    ) -> RoomResponse:
        if force_available:
            is_occupied = False
            noise_level = condition.noise_level if condition else None
            temperature = condition.temperature if condition else None
        else:
            is_occupied = condition.is_occupied if condition else False
            noise_level = condition.noise_level if condition else None
            temperature = condition.temperature if condition else None

        return RoomResponse(
            id=room.id,
            room_number=room.room_number,
            capacity=room.capacity,
            building_code=building.code if building else "?",
            building_name=building.name if building else "Ukendt",
            is_occupied=is_occupied,
            noise_level=noise_level,
            temperature=temperature,
            latitude=room.latitude,
            longitude=room.longitude,
            distance_meters=distance_meters,
        )

    def _room_base_query(self, min_capacity: Optional[int] = None):
        query = (
            self.db.query(Workroom, Building, RoomCondition)
            .outerjoin(Building, Building.id == Workroom.building_id)
            .outerjoin(RoomCondition, RoomCondition.room_id == Workroom.id)
        )
        if min_capacity is not None:
            query = query.filter(Workroom.capacity >= min_capacity)
        return query

    def get_all_rooms(self) -> List[RoomResponse]:
        rows = self._room_base_query().all()
        return [self._to_room_response(room, building, condition) for room, building, condition in rows]

    def get_available_rooms(self, min_capacity: int = 1) -> List[RoomResponse]:
        rows = (
            self._room_base_query(min_capacity)
            .filter(RoomCondition.id.is_not(None), RoomCondition.is_occupied.is_(False))
            .all()
        )
        return [
            self._to_room_response(room, building, condition, force_available=True)
            for room, building, condition in rows
        ]

    def get_nearest_available_rooms(
        self,
        device_latitude: float,
        device_longitude: float,
        min_capacity: int = 1,
        max_distance_km: float = 10.0,
    ) -> List[RoomResponse]:
        rows = (
            self._room_base_query(min_capacity)
            .filter(RoomCondition.id.is_not(None), RoomCondition.is_occupied.is_(False))
            .all()
        )
        max_distance_meters = max_distance_km * 1000
        results: List[Tuple[float, RoomResponse]] = []

        for room, building, condition in rows:
            distance = haversine_distance(
                device_latitude,
                device_longitude,
                room.latitude,
                room.longitude,
            )
            if distance <= max_distance_meters:
                results.append(
                    (
                        distance,
                        self._to_room_response(
                            room,
                            building,
                            condition,
                            distance_meters=distance,
                            force_available=True,
                        ),
                    )
                )

        results.sort(key=lambda x: x[0])
        return [response for _, response in results]

    def find_nearest_available_room(
        self,
        device_latitude: float,
        device_longitude: float,
        min_capacity: int = 1,
        max_distance_km: float = 10.0,
    ) -> Optional[Tuple[Workroom, float]]:
        rows = (
            self._room_base_query(min_capacity)
            .filter(RoomCondition.id.is_not(None), RoomCondition.is_occupied.is_(False))
            .all()
        )
        max_distance_meters = max_distance_km * 1000
        nearest_room: Optional[Workroom] = None
        nearest_distance = float("inf")

        for room, _, _ in rows:
            distance = haversine_distance(
                device_latitude,
                device_longitude,
                room.latitude,
                room.longitude,
            )
            if distance <= max_distance_meters and distance < nearest_distance:
                nearest_room = room
                nearest_distance = distance

        if not nearest_room:
            return None
        return nearest_room, nearest_distance


class BookingService:
    def __init__(self, db: Session):
        self.db = db

    def _find_room(self, room_id: int) -> Optional[Workroom]:
        return self.db.query(Workroom).filter(Workroom.id == room_id).first()

    def _find_conflicting_booking(self, room_id: int, start_time: datetime, end_time: datetime):
        return (
            self.db.query(Booking)
            .filter(
                and_(
                    Booking.room_id == room_id,
                    Booking.status == "confirmed",
                    Booking.start_time < end_time,
                    Booking.end_time > start_time,
                )
            )
            .with_for_update()
            .first()
        )
        
    def _set_room_occupied(self, room_id: int, occupied: bool) -> None:
        condition = (
            self.db.query(RoomCondition)
            .filter(RoomCondition.room_id == room_id)
            .first()
        )
        if condition:
            condition.is_occupied = occupied
            condition.updated_at = datetime.utcnow()
        else:
            # in case room has no row yet
            self.db.add(
                RoomCondition(
                    room_id=room_id,
                    is_occupied=occupied,
                    updated_at=datetime.utcnow(),
                )
            )   

    def create_booking(self, booking: BookingCreate) -> BookingResponse:
        try:
            room = self._find_room(booking.room_id)
            if not room:
                raise HTTPException(status_code=404, detail="Rum ikke fundet")

            existing_booking = self._find_conflicting_booking(
                booking.room_id,
                booking.start_time,
                booking.end_time,
            )
            if existing_booking:
                raise HTTPException(
                    status_code=409,
                    detail="Rummet er allerede booket i dette tidsrum",
                )

            new_booking = Booking(
                room_id=booking.room_id,
                student_id=booking.student_id,
                start_time=booking.start_time,
                end_time=booking.end_time,
                status="confirmed",
            )
            self.db.add(new_booking)
            self._set_room_occupied(new_booking.room_id, True)
            self.db.commit()
            self.db.refresh(new_booking)

            return BookingResponse(
                id=new_booking.id,
                room_id=new_booking.room_id,
                student_id=new_booking.student_id,
                start_time=new_booking.start_time,
                end_time=new_booking.end_time,
                status=new_booking.status,
                latitude=room.latitude,
                longitude=room.longitude,
            )
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def create_nearest_booking(self, booking_nearest: BookingNearestCreate) -> BookingResponse:
        try:
            nearest = RoomService(self.db).find_nearest_available_room(
                device_latitude=booking_nearest.device_latitude,
                device_longitude=booking_nearest.device_longitude,
                min_capacity=booking_nearest.min_capacity,
                max_distance_km=booking_nearest.max_distance_km,
            )
            if not nearest:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"No available rooms found within {booking_nearest.max_distance_km} km "
                        f"with capacity {booking_nearest.min_capacity}+"
                    ),
                )

            nearest_room, _ = nearest
            existing_booking = self._find_conflicting_booking(
                nearest_room.id,
                booking_nearest.start_time,
                booking_nearest.end_time,
            )
            if existing_booking:
                raise HTTPException(
                    status_code=409,
                    detail="Nearest room was just booked by another user. Try again to find next nearest room.",
                )

            new_booking = Booking(
                room_id=nearest_room.id,
                student_id=booking_nearest.student_id,
                start_time=booking_nearest.start_time,
                end_time=booking_nearest.end_time,
                status="confirmed",
            )
            self.db.add(new_booking)
            self._set_room_occupied(new_booking.room_id, True)
            self.db.commit()
            self.db.refresh(new_booking)

            return BookingResponse(
                id=new_booking.id,
                room_id=new_booking.room_id,
                student_id=new_booking.student_id,
                start_time=new_booking.start_time,
                end_time=new_booking.end_time,
                status=new_booking.status,
                latitude=nearest_room.latitude,
                longitude=nearest_room.longitude,
            )
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def get_bookings(self, room_id: Optional[int] = None):
        query = self.db.query(Booking, Workroom).join(Workroom, Workroom.id == Booking.room_id)
        if room_id is not None:
            query = query.filter(Booking.room_id == room_id)

        rows = query.all()
        return [
            BookingResponse(
                id=booking.id,
                room_id=booking.room_id,
                student_id=booking.student_id,
                start_time=booking.start_time,
                end_time=booking.end_time,
                status=booking.status,
                latitude=room.latitude,
                longitude=room.longitude,
            )
            for booking, room in rows
        ]

    def cancel_booking(self, booking_id: int):
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking ikke fundet")

        booking.status = "cancelled"
        self.db.commit()
        return {"message": "Booking annulleret"}


class SensorService:
    def __init__(self, db: Session):
        self.db = db

    def update_sensor_data(
        self,
        room_id: int,
        noise_level: Optional[float] = None,
        temperature: Optional[float] = None,
        is_occupied: Optional[bool] = None,
    ):
        condition = self.db.query(RoomCondition).filter(RoomCondition.room_id == room_id).first()
        if not condition:
            raise HTTPException(status_code=404, detail="Rum ikke fundet")

        if noise_level is not None:
            condition.noise_level = noise_level
        if temperature is not None:
            condition.temperature = temperature
        if is_occupied is not None:
            condition.is_occupied = is_occupied

        condition.updated_at = datetime.utcnow()
        self.db.commit()
        return {"message": "Sensor-data opdateret", "room_id": room_id}


class StudentService:
    def __init__(self, db: Session):
        self.db = db

    def create_student(self, student: StudentCreate):
        new_student = Student(sdu_id=student.sdu_id, name=student.name)
        self.db.add(new_student)
        self.db.commit()
        return {"message": "Studerende oprettet", "id": new_student.id}

    def get_students(self):
        students = self.db.query(Student).all()
        return [{"id": s.id, "sdu_id": s.sdu_id, "name": s.name} for s in students]


class BuildingService:
    def __init__(self, db: Session):
        self.db = db

    def get_buildings(self):
        buildings = self.db.query(Building).all()
        return [{"id": b.id, "name": b.name, "code": b.code} for b in buildings]
