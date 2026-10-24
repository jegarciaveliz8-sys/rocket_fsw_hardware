import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "flight_recorder.db")

def analyze_flight():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flight_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mission_id TEXT,
            timestamp REAL,
            lat REAL,
            lon REAL,
            altitude REAL,
            speed REAL,
            roll REAL,
            pitch REAL,
            yaw REAL,
            tvc_x REAL,
            tvc_y REAL,
            fsm_state TEXT
        )
    ''')
    conn.commit()

    df = pd.read_sql_query("SELECT timestamp, altitude, speed, roll, pitch, yaw, fsm_state FROM flight_logs", conn)
    
    if df.empty:
        print("Base de datos vacía. Generando datos de prueba de caja negra para demostración...")
        sample_data = []
        for t in range(0, 35):
            alt = round(50.0 * 4.0 * (t/35.0) * (1.0 - (t/35.0)), 2) if t < 35 else 0.0
            speed = 2200.0 if t < 30 else 0.0
            sample_data.append(('demo_mission', float(t), 14.7883, -90.1988, alt, speed, 0.0, 5.0, 0.0, 0.0, 0.0, 'BALISTIC_MIDCOURSE_GUIDANCE'))
        cursor.executemany("INSERT INTO flight_logs (mission_id, timestamp, lat, lon, altitude, speed, roll, pitch, yaw, tvc_x, tvc_y, fsm_state) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", sample_data)
        conn.commit()
        df = pd.read_sql_query("SELECT timestamp, altitude, speed, roll, pitch, yaw, fsm_state FROM flight_logs", conn)

    conn.close()

    print("=== ANÁLISIS DE CAJA NEGRA ODYSSEY-1 ===")
    print(f"Total de muestras analizadas: {len(df)}")
    print(f"Altitud máxima registrada: {df['altitude'].max():.2f} km")
    print(f"Velocidad máxima registrada: {df['speed'].max():.2f} km/h")

    plt.figure(figsize=(10, 6))
    
    plt.subplot(2, 1, 1)
    plt.plot(df['timestamp'], df['altitude'], label='Altitud (km)', color='blue', linewidth=2)
    plt.ylabel('Altitud MSL (km)')
    plt.title('ODYSSEY-1 - Telemetría de Vuelo Post-Análisis')
    plt.legend()
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.plot(df['timestamp'], df['speed'], label='Velocidad (km/h)', color='orange', linewidth=2)
    plt.xlabel('Tiempo de Misión (s)')
    plt.ylabel('Velocidad (km/h)')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("flight_analysis.png")
    print("Gráfica de análisis generada y guardada como 'flight_analysis.png'.")

if __name__ == "__main__":
    analyze_flight()
