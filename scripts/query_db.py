import sqlite3

DB_PATH = 'mission_database.db'

def query_mission_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("==================================================")
    print("     📊 CONSULTA DE TELEMETRÍA Y FDIR [Sanarate]  ")
    print("==================================================")
    
    # Consultar últimos registros de telemetría
    print("\n--- Últimos Registros de Telemetría (HIL) ---")
    cursor.execute("SELECT id, timestamp, altitude, velocity, thrust_cmd, battery_pct FROM telemetry_logs ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f"ID: {row[0]} | Fecha/Hora: {row[1]} | Alt: {row[2]}m | Vel: {row[3]}m/s | Empuje: {row[4]}N/kg | Batería: {row[5]}%")
    else:
        print("[AVISO] No hay registros de telemetría aún.")
        
    # Consultar eventos FDIR
    print("\n--- Eventos FDIR Registrados ---")
    cursor.execute("SELECT id, timestamp, event_type, status, details FROM fdir_events ORDER BY id DESC LIMIT 5")
    fdir_rows = cursor.fetchall()
    if fdir_rows:
        for frow in fdir_rows:
            print(f"ID: {frow[0]} | Fecha/Hora: {frow[1]} | Evento: {frow[2]} | Estado: {frow[3]} | Detalles: {frow[4]}")
    else:
        print("[AVISO] No hay eventos FDIR registrados todavía.")
        
    print("==================================================")
    conn.close()

if __name__ == "__main__":
    query_mission_data()
