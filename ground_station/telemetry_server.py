import socket
import struct
import time

def run_telemetry_server():
    print("=== INICIANDO SERVIDOR DE TELEMETRÍA Y CAJA NEGRA (UDP) ===")
    
    # Configuración de Socket UDP local
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("127.0.0.1", 5005))
    server_socket.settimeout(1.0)
    
    print("Escuchando paquetes en 127.0.0.1:5005...")
    
    flight_log = open("flight_blackbox.bin", "wb")
    
    try:
        start_time = time.time()
        while time.time() - start_time < 5.0: # Simula 5 segundos de escucha
            try:
                data, addr = server_socket.recvfrom(1024)
                flight_log.write(data)
                print(f"[RECV] Paquete recibido de {addr} | Tamaño: {len(data)} bytes")
            except socket.timeout:
                continue
    finally:
        flight_log.close()
        server_socket.close()
        print("=== SESIÓN DE TELEMETRÍA GUARDADA EN CAJA NEGRA (flight_blackbox.bin) ===")

if __name__ == "__main__":
    run_telemetry_server()
