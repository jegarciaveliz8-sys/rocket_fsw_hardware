import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
from datetime import datetime

# Configura tu puerto serie (ej. '/dev/ttyACM0' en Linux o 'COM3' en Windows)
PORT = "/dev/ttyACM0"
BAUD = 115200

timestamps = []
altitudes = []
accelerations = []
states = []

# Crear archivo CSV de respaldo en tierra
csv_filename = f"ground_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
csv_file = open(csv_filename, mode='w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["Timestamp_ms", "State", "Ax", "Ay", "Az", "Altitude_m"])

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
except Exception as e:
    print(f"Error al abrir puerto serie: {e}")
    exit(1)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

def update(frame):
    line = ser.readline().decode('utf-8', errors='ignore').strip()
    if line:
        parts = line.split(',')
        if len(parts) == 6:
            try:
                t = float(parts[0]) / 1000.0  # Segundos
                state = int(parts[1])
                ax_val = float(parts[4])     # Az (aceleración vertical)
                alt = float(parts[5])        # Altitud

                timestamps.append(t)
                altitudes.append(alt)
                accelerations.append(ax_val)
                states.append(state)

                # Escribir en respaldo local
                csv_writer.writerow(parts)
                csv_file.flush()

                # Limpiar y redibujar gráficos en vivo
                ax1.clear()
                ax1.plot(timestamps[-100:], altitudes[-100:], label="Altitud (m)", color="blue")
                ax1.set_ylabel("Altitud [m]")
                ax1.legend(loc="upper left")
                ax1.grid(True)

                ax2.clear()
                ax2.plot(timestamps[-100:], accelerations[-100:], label="Aceleración Z (Gs)", color="orange")
                ax2.set_xlabel("Tiempo [s]")
                ax2.set_ylabel("Aceleración [Gs]")
                ax2.legend(loc="upper left")
                ax2.grid(True)
            except ValueError:
                    pass

ani = FuncAnimation(fig, update, interval=50)
plt.tight_layout()
plt.show()

ser.close()
csv_file.close()
