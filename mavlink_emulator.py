import time
import math
from pymavlink import mavutil

# Configurar conexión de salida UDP hacia el servidor ODYSSEY-1 / GCS
master = mavutil.mavlink_connection('udpout:127.0.0.1:14550', source_system=255)
print("⛵ [SIMULADOR USV] Iniciando navegación autónoma en superficie (Barco A -> B)...")

# Coordenadas de inicio (Punto A)
lat_start = 14.7883
lon_start = -90.1988

# Coordenadas de destino (Punto B)
lat_end = 14.7950
lon_end = -90.1900

t = 0
phase = "STANDBY"

try:
    while True:
        t += 0.5
        
        # --- MÁQUINA DE ESTADOS DEL USV (BARCO) ---
        if t < 10:
            phase = "SYSTEMS INITIALIZED (Puerto A)"
            alt = 0.0
            lat = lat_start
            lon = lon_start
            vx, vy = 0, 0
            
        elif 10 <= t < 45:
            phase = "WATERWAY NAVIGATION (A ➔ B)"
            progress = (t - 10) / 35.0  # de 0 a 1
            alt = 0.0
            
            # Trayectoria fluvial con curva suave por corrientes de agua
            base_lat = lat_start + (lat_end - lat_start) * progress
            base_lon = lon_start + (lon_end - lon_start) * progress
            current_drift = math.sin(progress * math.math_constants if hasattr(math, 'math_constants') else math.pi * progress) * 0.001
            
            lat = base_lat + current_drift
            lon = base_lon
            vx, vy = 25, 20  # Nudos / velocidad reducida en agua
            
        elif 45 <= t < 65:
            phase = "STATION KEEPING / LOITER (En Destino B)"
            alt = 0.0
            # Pequeña deriva por corriente en el punto de destino
            lat = lat_end + math.sin(t * 0.5) * 0.0003
            lon = lon_end + math.cos(t * 0.5) * 0.0003
            vx, vy = 5, 5
            
        elif 65 <= t < 95:
            phase = "RETURN TO PORT (RTL Marino)"
            progress_back = (t - 65) / 30.0
            alt = 0.0
            lat = lat_end + (lat_start - lat_end) * progress_back
            lon = lon_end + (lon_start - lon_end) * progress_back
            vx, vy = -25, -20
            
        else:
            phase = "MOORED / DOCKED (Misión Marina Concluida)"
            alt = 0.0
            lat = lat_start
            lon = lon_start
            vx, vy = 0, 0

        # Imprimir telemetría en terminal
        print(f"⛵ [USV Fase: {phase}] Alt: {alt:.1f}m | Lat: {lat:.4f} | Lon: {lon:.4f}")

        # Enviar posición global MAVLink
        master.mav.global_position_int_send(
            time_boot_ms=int(t * 1000),
            lat=int(lat * 1e7),
            lon=int(lon * 1e7),
            alt=int(alt * 1000),
            relative_alt=int(alt * 1000),
            vx=vx, vy=vy, vz=0,
            hdg=int((t * 5) % 360)
        )
        
        # Enviar actitud simulando el oleaje del agua (balanceo constante de rolido y cabeceo)
        master.mav.attitude_send(
            time_boot_ms=int(t * 1000),
            roll=math.sin(t * 3) * 0.08,   # Efecto de olas lateral (Roll)
            pitch=math.cos(t * 2.5) * 0.05, # Efecto de proa/popa (Pitch)
            yaw=t * 0.05,
            rollspeed=0.0,
            pitchspeed=0.0,
            yawspeed=0.0
        )

        time.sleep(0.5)
        
except KeyboardInterrupt:
    print("\n🛑 Simulación de USV detenida por el operador.")
