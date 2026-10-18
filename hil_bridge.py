import serial
import time
import sys

# Configura el puerto serial (ejemplo: '/dev/pts/5' para Teensy/Arduino en Linux)
SERIAL_PORT = "/dev/pts/5" 
BAUD_RATE = 115200

def run_hil_monitor():
    print(f"[HIL Bridge] Conectando al hardware de vuelo en {SERIAL_PORT}...")
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1.0)
        time.sleep(2) # Esperar reseteo de la placa
        
        print("[HIL Bridge] Conexión establecida. Escuchando telemetría de vuelo (Presiona Ctrl+C para salir)...")
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"[HW Telemetry] {line}")
            time.sleep(0.001)

    except serial.SerialException:
        print(f"[Error] No se pudo abrir el puerto {SERIAL_PORT}. Asegúrate de que la placa esté conectada o ajusta el nombre del puerto.")
    except KeyboardInterrupt:
        print("\n[HIL Bridge] Monitoreo finalizado.")

if __name__ == "__main__":
    run_hil_monitor()
