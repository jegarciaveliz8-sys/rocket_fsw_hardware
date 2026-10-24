import time
import math
from pymavlink import mavutil

print("Iniciando Simulador Virtual MAVLink (SITL)...")

# Enviar telemetría hacia la GCS (puerto 14550)
telemetry_conn = mavutil.mavlink_connection('udpout:127.0.0.1:14550', source_system=1, source_component=1)

# Escuchar comandos de control desde la GCS (puerto 14556)
command_conn = mavutil.mavlink_connection('udpin:127.0.0.1:14556', source_system=1, source_component=1)

is_armed = False
altitude = 0.0
lat = 14.7883 * 1e7
lon = -90.1988 * 1e7

start_time = time.monotonic()
print("Simulador activo: transmitiendo telemetría y escuchando comandos de control...")

last_telemetry = 0

while True:
    current_time = time.monotonic()
    time_boot_ms = int((current_time - start_time) * 1000) & 0xFFFFFFFF

    # Enviar paquetes de telemetría cada 0.1 segundos
    if current_time - last_telemetry >= 0.1:
        last_telemetry = current_time
        
        base_mode = 81 if is_armed else 65
        telemetry_conn.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_QUADROTOR,
            mavutil.mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA,
            base_mode,
            0,
            mavutil.mavlink.MAV_STATE_ACTIVE if is_armed else mavutil.mavlink.MAV_STATE_STANDBY
        )

        if is_armed and altitude < 15.0:
            altitude += 0.2  # Simular ascenso gradual al armar/despegar
        elif not is_armed:
            altitude = max(0.0, altitude - 0.2)

        telemetry_conn.mav.global_position_int_send(
            time_boot_ms,
            int(lat),
            int(lon),
            int(altitude * 1000),
            int(altitude * 1000),
            0, 0, 0, 0
        )

        telemetry_conn.mav.attitude_send(
            time_boot_ms,
            0.0, 0.0, 0.0,
            0.0, 0.0, 0.0
        )

    # Procesar comandos entrantes de la GCS
    msg = command_conn.recv_match(blocking=False)
    if msg:
        msg_type = msg.get_type()
        if msg_type == 'COMMAND_LONG':
            print(f"📥 [SITL RECEPTOR] Comando ID: {msg.command} | Parámetros: [{msg.param1}, {msg.param2}]")
            if msg.command == 400: # ARM / DISARM
                is_armed = (msg.param1 == 1.0)
                status_str = "ARMADO 🟢" if is_armed else "DESARMADO 🟡"
                print(f"🚁 Estado del vehículo cambiado a: {status_str}")
            elif msg.command == 22: # TAKEOFF
                is_armed = True
                print(f"🚀 [SITL] ¡Secuencia de despegue iniciada a {msg.param1}m!")

    time.sleep(0.01)
