-- SDU Workroom Finder - Database Schema
-- This runs automatically when the container starts for the first time

-- Buildings
CREATE TABLE buildings (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL
);

-- Workrooms
CREATE TABLE workrooms (
    id SERIAL PRIMARY KEY,
    building_id INTEGER REFERENCES buildings(id),
    room_number VARCHAR(20) NOT NULL,
    capacity INTEGER NOT NULL,
    is_available BOOLEAN DEFAULT true
);

-- Students
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    sdu_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL
);

-- Gadgets
CREATE TABLE gadgets (
    id SERIAL PRIMARY KEY,
    device_code VARCHAR(50) UNIQUE NOT NULL,
    student_id INTEGER REFERENCES students(id),
    battery_level INTEGER DEFAULT 100
);

-- Room conditions (sensor data)
CREATE TABLE room_conditions (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES workrooms(id),
    is_occupied BOOLEAN DEFAULT false,
    noise_level DECIMAL(5,2),
    temperature DECIMAL(4,1),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Search requests (lifelogging)
CREATE TABLE search_requests (
    id SERIAL PRIMARY KEY,
    gadget_id INTEGER REFERENCES gadgets(id),
    requested_capacity INTEGER NOT NULL,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id),
    room_id INTEGER REFERENCES workrooms(id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data
INSERT INTO buildings (name, code) VALUES 
    ('Teknisk Fakultet', 'TEK'),
    ('Naturvidenskabeligt Fakultet', 'NAT'),
    ('Bibliotek', 'BIB');

INSERT INTO workrooms (building_id, room_number, capacity) VALUES 
    (1, 'Ø21-601a', 6),
    (1, 'Ø21-601b', 6),
    (1, 'Ø21-602', 4),
    (2, 'N21-401', 4),
    (2, 'N21-402', 8),
    (3, 'BIB-G01', 4),
    (3, 'BIB-101', 6);

INSERT INTO room_conditions (room_id, is_occupied, noise_level, temperature) VALUES 
    (1, false, 35.0, 21.5),
    (2, true, 45.0, 22.0),
    (3, false, 30.0, 20.5),
    (4, false, 38.0, 21.0),
    (5, true, 50.0, 23.0),
    (6, false, 25.0, 20.0),
    (7, false, 28.0, 21.5);
