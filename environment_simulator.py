import time
import math
import serial

# Usaremos el otro extremo del enlace virtual socat para enviar datos a la placa
SERIAL_PORT = "/dev/pts/6"
BAUD_RATE = 115200

def run_environment():
    print(f"[Simulador Físico] Iniciando entorno virtual HIL en {SERIAL_PORT}...")
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        time.sleep(1)
        
        t = 0.0
        dt = 0.05  # Tasa de actualización ambiental (20 Hz)
        
        print("[Simulador Físico] Transmitiendo datos de sensores virtuales (Ctrl+C para salir)...")
        while True:
            # Simular aceleración y altitud basadas en el tiempo de vuelo
            altitude = 0.5 * 15.0 * (t ** 2) if t < 4.0 else 120.0 + 30.0 * (t - 4.0)
            accel_z = 15.0 if t < 4.0 else 0.0
            
            # Formar el paquete de telemetría de sensores simulados (IMU / GPS)
            telemetry_packet = f"ALT:{altitude:.2f},ACCZ:{accel_z:.2f},T:{t:.2f}\n"
            
            ser.write(telemetry_packet.encode('utf-8'))
            print(f"[Enviado a FSW] {telemetry_packet.strip()}")
            
            t += dt
            time.sleep(dt)

    except serial.SerialException as e:
        print(f"[Error de Puerto] {e}")
    except KeyboardInterrupt:
        print("\n[Simulador Físico] Simulación detenida.")

if __name__ == "__main__":
    run_environment()
