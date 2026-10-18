import sqlite3
import os

DB_PATH = 'mission_database.db'

def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telemetry_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mission_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            altitude REAL,
            velocity REAL,
            acceleration REAL
        )
    ''')
    
    # Insertar datos de vuelo de prueba si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM telemetry_logs")
    if cursor.fetchone()[0] == 0:
        test_data = [
            ('MISSIO_001', 10.5, 12.0, 2.1),
            ('MISSIO_001', 45.2, 35.0, 4.2),
            ('MISSIO_001', 120.8, 58.5, 5.8),
            ('MISSIO_001', 150.0, 60.0, 1.2),
            ('MISSIO_001', 148.2, 0.0, -0.5)
        ]
        cursor.executemany('''
            INSERT INTO telemetry_logs (mission_id, altitude, velocity, acceleration)
            VALUES (?, ?, ?, ?)
        ''', test_data)
        print("[INFO] Datos de telemetría de prueba registrados en 'mission_database.db'.")
    else:
        print("[INFO] La base de datos ya contiene registros de telemetría.")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
