import socket
import struct
import time
import threading
import os

def telemetry_server_thread(stop_event):
    print("[SERVIDOR] Iniciando escucha de telemetría UDP en 127.0.0.1:5005...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("127.0.0.1", 5005))
    server_socket.settimeout(0.5)
    
    os.makedirs("ground_station", exist_ok=True)
    with open("ground_station/flight_blackbox.bin", "wb") as flight_log:
        while not stop_event.is_set():
            try:
                data, _ = server_socket.recvfrom(1024)
                flight_log.write(data)
            except socket.timeout:
                continue
    server_socket.close()
    print("[SERVIDOR] Caja negra guardada exitosamente.")

def flight_simulation_client():
    print("[COHETE] Iniciando transmisión de telemetría de vuelo (SITL)...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ("127.0.0.1", 5005)
    
    dt = 0.05
    for i in range(100):
        t = i * dt
        # Simulación de variables de vuelo
        altitude = max(0.0, 150.0 * (1.0 - (t - 2.5)**2 / 6.25)) if t <= 5.0 else 0.0
        velocity = 60.0 - (9.81 * t)
        acceleration = 5.8 if t < 2.5 else -1.5
        
        # Estructura binaria estricta (igual al protocolo FSW)
        packet = struct.pack("<BBIB5fH", 0xAA, 0x55, int(t * 1000), 2, 0.1, 0.05, acceleration, altitude, velocity, 0x1234)
        client_socket.sendto(packet, server_address)
        time.sleep(0.05)
        
    client_socket.close()
    print("[COHETE] Simulación de vuelo finalizada.")

if __name__ == "__main__":
    print("=== INICIANDO MISIÓN VIRTUAL INTEGRADA ===")
    stop_event = threading.Event()
    
    # Lanzar servidor en un hilo secundario
    server_thread = threading.Thread(target=telemetry_server_thread, args=(stop_event,))
    server_thread.start()
    
    time.sleep(0.2) # Esperar arranque del servidor
    
    # Ejecutar simulación de vuelo cliente
    flight_simulation_client()
    
    # Detener servidor
    time.sleep(0.5)
    stop_event.set()
    server_thread.join()
    print(">>> MISIÓN VIRTUAL COMPLETADA CON ÉXITO EXTREMO <<<")
