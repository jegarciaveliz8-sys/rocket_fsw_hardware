import time
import math
from pymavlink import mavutil

# Configurar conexión de salida UDP hacia el servidor ODYSSEY-1
master = mavutil.mavlink_connection('udpout:127.0.0.1:14550', source_system=255)
print("🚁 Emulador de Dron Autónomo MAVLink activo...")

lat = 14.7883 * 1e7
lon = -90.1988 * 1e7
alt = 100.0  # Altitud inicial en metros
t = 0

try:
    while True:
        t += 0.1
        # Simular movimiento circular del dron
        lat += int(math.sin(t * 0.5) * 50)
        lon += int(math.cos(t * 0.5) * 50)
        alt = 50.0 + math.sin(t) * 10.0 # Oscilación de altitud realista para un dron
        
        # Enviar posición global (GLOBAL_POSITION_INT)
        master.mav.global_position_int_send(
            time_boot_ms=int(t * 1000),
            lat=int(lat),
            lon=int(lon),
            alt=int(alt * 1000),         # Altitud MSL en milímetros
            relative_alt=int(alt * 1000), # Altitud AGL en milímetros
            vx=200, vy=100, vz=0,
            hdg=0
        )
        
        # Enviar actitud del dron (ATTITUDE)
        master.mav.attitude_send(
            time_boot_ms=int(t * 1000),
            roll=math.sin(t * 2) * 0.1,
            pitch=math.cos(t * 2) * 0.1,
            yaw=t * 0.1,
            rollspeed=0.0,
            pitchspeed=0.0,
            yawspeed=0.0
        )

        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n🛑 Emulación detenida.")
