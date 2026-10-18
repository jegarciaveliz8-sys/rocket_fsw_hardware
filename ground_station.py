import sys
import time
import serial
import threading
import queue
import math
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

SERIAL_PORT = "/dev/pts/3" 
BAUD_RATE = 115200

data_queue = queue.Queue()
times = []
altitudes = []
commands = []

def serial_listener():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"[Estación de Tierra] Conectado exitosamente a {SERIAL_PORT}")
        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                parts = line.split(',')
                if len(parts) >= 2:
                    try:
                        t = float(parts[0])
                        alt = float(parts[1])
                        cmd = float(parts[2]) if len(parts) > 2 else 0.0
                        data_queue.put((t, alt, cmd))
                    except ValueError:
                        pass
    except Exception as e:
        print(f"[Modo Simulación / Desconectado] No se pudo abrir {SERIAL_PORT}. Usando datos de respaldo...")
        sim_t = 0.0
        while True:
            sim_t += 0.05
            sim_alt = 500.0 * (1.0 - math.exp(-0.2 * sim_t))
            data_queue.put((sim_t, sim_alt, 1500.0))
            time.sleep(0.05)

t_thread = threading.Thread(target=serial_listener, daemon=True)
t_thread.start()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
fig.suptitle('Estación de Tierra GNC - Cohete Experimental (En Vivo)', fontsize=14, fontweight='bold')

def update_plot(frame):
    while not data_queue.empty():
        t, alt, cmd = data_queue.get()
        times.append(t)
        altitudes.append(alt)
        commands.append(cmd)
        
        if len(times) > 200:
            times.pop(0)
            altitudes.pop(0)
            commands.pop(0)

    ax1.clear()
    ax1.plot(times, altitudes, color='tab:blue', linewidth=2, label='Altitud (m)')
    ax1.set_ylabel('Altitud [m]')
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend(loc='upper left')

    ax2.clear()
    ax2.plot(times, commands, color='tab:red', linewidth=1.5, label='Comando TVC / PWM')
    ax2.set_xlabel('Tiempo de Vuelo [s]')
    ax2.set_ylabel('PWM / Control')
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.legend(loc='upper left')

ani = FuncAnimation(fig, update_plot, interval=50)
plt.tight_layout()
plt.show()
