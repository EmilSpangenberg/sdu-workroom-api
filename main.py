"""
SDU Workroom Finder - API with Proper Concurrent Access
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from datetime import datetime

# ============================================
# DATABASE SETUP - With Connection Pooling
# ============================================

DATABASE_URL = "postgresql://postgres:postgres123@localhost:5432/sdu_workrooms"

# Connection pool: Håndterer mange samtidige forbindelser
engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # 10 forbindelser klar til brug
    max_overflow=20,       # Op til 20 ekstra ved spidsbelastning
    pool_pre_ping=True,    # Tjek om forbindelse virker før brug
    pool_recycle=3600,     # Genopret forbindelser hver time
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================
# DATABASE DEPENDENCY - Proper Session Handling
# ============================================

def get_db():
    """
    Opretter en database session per request.
    Lukker automatisk når request er færdig.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================
# DATABASE MODELS
# ============================================

class Building(Base):
    __tablename__ = "buildings"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    code = Column(String(10), unique=True)


class Workroom(Base):
    __tablename__ = "workrooms"
    id = Column(Integer, primary_key=True)
    building_id = Column(Integer, ForeignKey("buildings.id"))
    room_number = Column(String(20))
    capacity = Column(Integer)
    is_available = Column(Boolean, default=True)


class RoomCondition(Base):
    __tablename__ = "room_conditions"
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("workrooms.id"))
    is_occupied = Column(Boolean, default=False)
    noise_level = Column(Float)
    temperature = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    sdu_id = Column(String(20), unique=True)
    name = Column(String(100))


class Gadget(Base):
    __tablename__ = "gadgets"
    id = Column(Integer, primary_key=True)
    device_code = Column(String(50), unique=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    battery_level = Column(Integer, default=100)


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("workrooms.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(20), default="confirmed")
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================
# PYDANTIC MODELS
# ============================================

class RoomResponse(BaseModel):
    id: int
    room_number: str
    capacity: int
    building_code: str
    building_name: str
    is_occupied: bool
    noise_level: Optional[float]
    temperature: Optional[float]

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    room_id: int
    student_id: int
    start_time: datetime
    end_time: datetime


class BookingResponse(BaseModel):
    id: int
    room_id: int
    student_id: int
    start_time: datetime
    end_time: datetime
    status: str

    class Config:
        from_attributes = True


class StudentCreate(BaseModel):
    sdu_id: str
    name: str


# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
    title="SDU Workroom Finder API",
    description="Find ledige grupperum på SDU campus",
    version="1.0.0"
)


# ============================================
# API ENDPOINTS - With Dependency Injection
# ============================================

@app.get("/")
def home():
    return {"status": "online", "message": "SDU Workroom Finder API kører!"}


@app.get("/rooms", response_model=List[RoomResponse])
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
            temperature=condition.temperature if condition else None
        ))
    
    return results


@app.get("/rooms/available")
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
                temperature=condition.temperature
            ))
    
    return results


# ============================================
# BOOKING WITH CONCURRENCY CONTROL
# ============================================

@app.post("/bookings", response_model=BookingResponse)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    """
    Opret booking med concurrent access kontrol.
    Bruger SELECT ... FOR UPDATE til at låse rækken.
    """
    from sqlalchemy import and_
    
    # Start transaction
    try:
        # Tjek om rummet allerede er booket i tidsrummet
        # FOR UPDATE låser rækkerne så andre må vente
        existing_booking = db.query(Booking).filter(
            and_(
                Booking.room_id == booking.room_id,
                Booking.status == "confirmed",
                Booking.start_time < booking.end_time,
                Booking.end_time > booking.start_time
            )
        ).with_for_update().first()  # <-- LÅSER RÆKKEN
        
        if existing_booking:
            raise HTTPException(
                status_code=409,  # Conflict
                detail="Rummet er allerede booket i dette tidsrum"
            )
        
        # Opret booking
        new_booking = Booking(
            room_id=booking.room_id,
            student_id=booking.student_id,
            start_time=booking.start_time,
            end_time=booking.end_time,
            status="confirmed"
        )
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)
        
        return BookingResponse(
            id=new_booking.id,
            room_id=new_booking.room_id,
            student_id=new_booking.student_id,
            start_time=new_booking.start_time,
            end_time=new_booking.end_time,
            status=new_booking.status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()  # Rul tilbage ved fejl
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/bookings")
def get_bookings(room_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Booking)
    if room_id:
        query = query.filter(Booking.room_id == room_id)
    return query.all()


@app.delete("/bookings/{booking_id}")
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking ikke fundet")
    
    booking.status = "cancelled"
    db.commit()
    return {"message": "Booking annulleret"}


# ============================================
# SENSOR UPDATE WITH OPTIMISTIC LOCKING
# ============================================

@app.post("/sensors/update")
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


# ============================================
# OTHER ENDPOINTS
# ============================================

@app.get("/buildings")
def get_buildings(db: Session = Depends(get_db)):
    buildings = db.query(Building).all()
    return [{"id": b.id, "name": b.name, "code": b.code} for b in buildings]


@app.post("/students")
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    new_student = Student(sdu_id=student.sdu_id, name=student.name)
    db.add(new_student)
    db.commit()
    return {"message": "Studerende oprettet", "id": new_student.id}


@app.get("/students")
def get_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return [{"id": s.id, "sdu_id": s.sdu_id, "name": s.name} for s in students]


# ============================================
# RUN
# ============================================

if __name__ == "__main__":
    import uvicorn
    print("Starting SDU Workroom Finder API...")
    print("Åbn http://localhost:8000/docs i din browser")
    uvicorn.run(app, host="0.0.0.0", port=8000)