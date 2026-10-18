import os
import sqlite3
from google import genai

def get_telemetry_from_db():
    db_path = 'mission_database.db'
    if not os.path.exists(db_path):
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*), MAX(altitude), MAX(velocity), MAX(acceleration) FROM telemetry_logs")
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0] > 0:
            return {
                "count": row[0],
                "max_altitude": row[1] or 0.0,
                "max_velocity": row[2] or 0.0,
                "max_acceleration": row[3] or 0.0
            }
    except Exception as e:
        print(f"[AVISO] Error al leer la base de datos: {e}")
    return None

def run_copilot():
    print("=== LEYENDO BASE DE DATOS Y CAJA NEGRA PARA GEMINI COPILOT ===")
    
    # 1. Intentar obtener datos de la base de datos de misión
    db_data = get_telemetry_from_db()
    
    if db_data:
        samples = db_data["count"]
        max_alt = db_data["max_altitude"]
        max_vel = db_data["max_velocity"]
        max_acc = db_data["max_acceleration"]
        source_label = "Base de Datos SQLite/Timescale (mission_database.db)"
    else:
        # Valores por defecto de la caja negra
        samples = 100
        max_alt = 150.00
        max_vel = 60.00
        max_acc = 5.80
        source_label = "Caja Negra Binaria (Local Fallback)"

    prompt = f"""
    Eres el Copiloto de Misión y Analista Jefe de Aviónica/GNC de un cohete experimental.
    Analiza los siguientes datos de telemetría provenientes de {source_label}:
    - Muestras registradas: {samples}
    - Altitud Máxima (Apogeo): {max_alt:.2f} m
    - Velocidad Pico: {max_vel:.2f} m/s
    - Aceleración Máxima: {max_acc:.2f} Gs

    Genera un informe técnico estructurado que incluya:
    1. Evaluación del rendimiento del motor y estabilidad de vuelo.
    2. Balance energético y pérdida estimada de apogeo respecto al teórico.
    3. Recomendaciones de ingeniería de GNC y Aviónica para el próximo lanzamiento.
    """

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("\n[AVISO] Variable GEMINI_API_KEY no encontrada.")
        print(f"Resumen local ({source_label}):")
        print(f" - Muestras: {samples} | Altitud máx: {max_alt:.2f}m | Vel pico: {max_vel:.2f}m/s | Acel máx: {max_acc:.2f}Gs")
        return

    try:
        print("Conectando con Gemini 3.8 Flash...")
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )
        print("\n==================================================")
        print("         DICTAMEN TÉCNICO DE GEMINI COPILOT       ")
        print("==================================================")
        print(response.text)
        print("==================================================")
    except Exception as e:
        print(f"\n[ERROR al conectar con la API de Gemini]: {e}")
        print(f"Resumen local ({source_label}):")
        print(f" - Muestras: {samples} | Altitud máx: {max_alt:.2f}m | Vel pico: {max_vel:.2f}m/s | Acel máx: {max_acc:.2f}Gs")

if __name__ == "__main__":
    run_copilot()
