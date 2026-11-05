import sqlite3
from datetime import datetime

DB_NAME = "odyssey_telemetry.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flight_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            flight_time REAL,
            altitude REAL,
            velocity REAL,
            lat REAL,
            lon REAL,
            chamber_pressure REAL,
            battery_pct REAL,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_telemetry(data: dict):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO flight_logs (timestamp, flight_time, altitude, velocity, lat, lon, chamber_pressure, battery_pct, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().isoformat(),
        data.get("time", 0.0),
        data.get("altitude", 0.0),
        data.get("velocity", 0.0),
        data.get("lat", 14.7883),
        data.get("lon", -90.1988),
        data.get("chamber_pressure", 15.4),
        data.get("battery_pct", 100.0),
        data.get("status", "STANDBY")
    ))
    conn.commit()
    conn.close()
