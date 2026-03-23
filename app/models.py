from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String

from app.database import Base


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
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)


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
