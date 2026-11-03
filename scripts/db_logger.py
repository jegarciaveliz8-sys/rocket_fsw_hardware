import sqlite3
import datetime
import os

DB_PATH = 'mission_database.db'

def init_database():
    """Inicializa las tablas de telemetría HIL y registros de eventos FDIR."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Tabla principal de telemetría
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telemetry_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mission_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            altitude REAL,
            velocity REAL,
            thrust_cmd REAL,
            wind_disturbance REAL,
            battery_pct REAL
        )
    ''')
    
    # 2. Tabla para eventos de falla y diagnóstico FDIR
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fdir_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT,
            status TEXT,
            details TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("[INFO] Base de datos 'mission_database.db' estructurada correctamente para HIL y FDIR.")

def log_telemetry(mission_id, alt, vel, thrust, wind, battery):
    """Inserta una muestra del bucle H-infinito en la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO telemetry_logs (mission_id, altitude, velocity, thrust_cmd, wind_disturbance, battery_pct)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (mission_id, alt, vel, thrust, wind, battery))
    conn.commit()
    conn.close()

def log_fdir_event(event_type, status, details=""):
    """Registra alertas o recuperaciones FDIR (ej: rf_blackout, low_battery)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO fdir_events (event_type, status, details)
        VALUES (?, ?, ?)
    ''', (event_type, status, details))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
