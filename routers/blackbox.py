import os
import csv
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Archivo único por sesión de ejecución
timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filepath = os.path.join(LOG_DIR, f"flight_log_{timestamp_str}.csv")

# Inicializar archivo CSV con cabeceras
with open(log_filepath, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "time_sec", "altitude", "velocity", "chamber_pressure", "battery_pct", "lat", "lon", "status"])

def log_telemetry_packet(packet: dict):
    """Inserta una línea de telemetría en la caja negra CSV."""
    try:
        with open(log_filepath, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                packet.get("timestamp", 0),
                packet.get("altitude", 0),
                packet.get("velocity", 0),
                packet.get("chamber_pressure", 0),
                packet.get("battery_pct", 0),
                packet.get("lat", 0),
                packet.get("lon", 0),
                packet.get("status", "UNKNOWN")
            ])
    except Exception as e:
        print(f"⚠️ [BLACKBOX] Error al guardar registro: {e}")
