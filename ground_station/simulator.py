import serial
import time
import sys

# Configura el puerto serie (en Linux puedes usar un par virtual tipo /dev/tve0 o tu puerto real)
PORT = "/dev/ttyACM0"
BAUD = 115200

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
except Exception as e:
    print(f"No se pudo abrir el puerto {PORT}: {e}")
    print("Asegúrate de que la Teensy esté conectada o usa un puerto virtual (ej. socat).")
    sys.exit(1)

print("Iniciando simulación de vuelo HIL...")
print("Fases: IDLE -> BOOST -> COAST -> APOGEE -> RECOVERY")

start_time = time.time()

def send_frame(state, ax, ay, az, altitude):
    timestamp = int((time.time() - start_time) * 1000)
    # Formato exacto que espera el firmware / estación terrena: Timestamp, State, Ax, Ay, Az, Altitude
    frame = f"{timestamp},{state},{ax:.2f},{ay:.2f},{az:.2f},{altitude:.2f}\n"
    ser.write(frame.encode('utf-8'))
    print(f"Enviado: {frame.strip()}")

try:
    # 1. Fase IDLE (Cohete en plataforma)
    print("\n--- Fase: IDLE ---")
    for _ in range(20):
        send_frame(state=0, ax=0.0, ay=0.0, az=1.0, altitude=0.0)
        time.sleep(0.1)

    # 2. Fase BOOST (Lanzamiento y aceleración fuerte)
    print("\n--- Fase: BOOST ---")
    for i in range(15):
        az_val = 5.0 + (i * 0.5)
        alt_val = i * 2.0
        send_frame(state=1, ax=0.2, ay=0.1, az=az_val, altitude=alt_val)
        time.sleep(0.1)

    # 3. Fase COAST (Inercia hacia arriba, desacelerando)
    print("\n--- Fase: COAST (Ascenso libre) ---")
    current_alt = 30.0
    for i in range(30):
        current_alt += (10.0 - (i * 0.3)) # Va desacelerando la subida
        send_frame(state=2, ax=0.0, ay=0.0, az=0.2, altitude=max(0, current_alt))
        time.sleep(0.1)

    # 4. Fase APOGEE (Punto más alto, inversión y despliegue)
    print("\n--- Fase: APOGEE (Despliegue de pirotecnia) ---")
    for _ in range(10):
        send_frame(state=3, ax=0.0, ay=0.0, az=-0.5, altitude=current_alt)
        time.sleep(0.1)

    # 5. Fase RECOVERY (Descenso con paracaídas)
    print("\n--- Fase: RECOVERY (Descenso) ---")
    for i in range(30):
        current_alt = max(0.0, current_alt - 5.0)
        send_frame(state=4, ax=0.0, ay=0.0, az=1.0, altitude=current_alt)
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nSimulación interrumpida por el usuario.")

ser.close()
print("Simulación finalizada.")
