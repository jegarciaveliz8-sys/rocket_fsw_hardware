import time
import requests

FASTAPI_ENDPOINT = "http://127.0.0.1:8000/api/dji/telemetry"

print("🛸 [DJI SDK SIMULATOR] Iniciando emulador de telemetría comercial...")

lat_start = 14.7883
lon_start = -90.1988
lat_end = 14.7950
lon_end = -90.1900

t = 0

try:
    while True:
        t += 0.5
        progress = (t % 40) / 40.0
        
        if (t // 40) % 2 == 0:
            current_lat = lat_start + (lat_end - lat_start) * progress
            current_lon = lon_start + (lon_end - lon_start) * progress
            alt = 30.0 * progress
            speed = 8.5
        else:
            current_lat = lat_end + (lat_start - lat_end) * progress
            current_lon = lon_end + (lon_start - lon_end) * progress
            alt = max(0.0, 30.0 * (1.0 - progress))
            speed = 0.0 if alt == 0 else 8.5

        payload = {
            "latitude": round(current_lat, 7),
            "longitude": round(current_lon, 7),
            "altitude_meters": round(alt, 2),
            "speed_ms": speed,
            "pitch": -1.5 if speed > 0 else 0.0,
            "roll": 0.5,
            "yaw": round((t * 10) % 360, 1)
        }

        try:
            response = requests.post(FASTAPI_ENDPOINT, json=payload, timeout=0.2)
            if response.status_code == 200:
                print(f"📡 [SDK Bridge] Lat: {current_lat:.4f} | Lon: {current_lon:.4f} | Alt: {alt:.1f}m | Spd: {speed}m/s")
        except requests.exceptions.RequestException:
            print("⚠️ [SDK Bridge] Esperando conexión con FastAPI en http://127.0.0.1:8000...")

        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n🛑 Emulador de SDK detenido por el operador.")
