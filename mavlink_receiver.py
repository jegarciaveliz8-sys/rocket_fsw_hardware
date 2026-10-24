from pymavlink import mavutil

print("Iniciando receptor MAVLink en udp:127.0.0.1:14550...")
connection = mavutil.mavlink_connection('udpin:127.0.0.1:14550')

print("Escuchando comandos y paquetes en tiempo real...")

while True:
    msg = connection.recv_match(blocking=True)
    if not msg:
        continue
    
    msg_type = msg.get_type()
    if msg_type == 'COMMAND_LONG':
        print(f"📥 [COMANDO RECIBIDO] ID: {msg.command} | Parámetros: [{msg.param1}, {msg.param2}, {msg.param3}, {msg.param4}, {msg.param5}, {msg.param6}, {msg.param7}]")
    else:
        print(f"📦 Paquete MAVLink recibido: {msg_type}")
