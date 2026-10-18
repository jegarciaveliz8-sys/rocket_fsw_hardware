import serial
import json
import time
import random

try:
    ser = serial.Serial('/tmp/ttyV1', 115200)
    print("Emulador HIL Avanzado iniciado en /tmp/ttyV1...")
except Exception as e:
    print(f"Error abriendo puerto virtual: {e}. Ejecuta socat primero.")
    exit(1)

mission_time = 0
try:
    while True:
        mission_time += 1
        altitude_noise = random.uniform(-0.1, 0.1)
        velocity_noise = random.uniform(-1.0, 1.0)
        
        payload = {
            "time": mission_time,
            "altitude": round((mission_time * 0.4) + altitude_noise, 2),
            "velocity": round((mission_time * 70.0) + velocity_noise, 1),
            "vibration": round(random.uniform(0.02, 0.15), 3),
            "status": "HIL MOCK ADVANCED"
        }
        ser.write((json.dumps(payload) + "\n").encode('utf-8'))
        print(f"Enviado HIL T+{mission_time}: Alt={payload['altitude']}km | Vib={payload['vibration']}G")
        time.sleep(1.0)
except KeyboardInterrupt:
    ser.close()
    print("Emulador avanzado detenido.")
