import struct

# Formato de empaquetado binario little-endian:
# < (little-endian)
# 2B (dos bytes de sync: 0xAA, 0x55)
# I (uint32_t timestamp)
# B (uint8_t flight_state)
# 5f (cinco floats: ax, ay, az, alt, vel)
# H (uint16_t checksum)
PACKET_FORMAT = "<BBIB5fH"
PACKET_SIZE = struct.calcsize(PACKET_FORMAT)

def parse_telemetry_stream(raw_stream_bytes):
    packets = []
    buffer = bytearray(raw_stream_bytes)
    
    while len(buffer) >= PACKET_SIZE:
        # Buscar bytes de sincronización 0xAA 0x55
        if buffer[0] == 0xAA and buffer[1] == 0x55:
            packet_bytes = buffer[:PACKET_SIZE]
            unpacked = struct.unpack(PACKET_FORMAT, packet_bytes)
            
            packet = {
                "timestamp_ms": unpacked[2],
                "flight_state": unpacked[3],
                "ax": unpacked[4],
                "ay": unpacked[5],
                "az": unpacked[6],
                "altitude": unpacked[7],
                "velocity": unpacked[8],
                "checksum": unpacked[9]
            }
            packets.append(packet)
            del buffer[:PACKET_SIZE]
        else:
            # Desplazar el buffer si hay pérdida de trama
            del buffer[0]
            
    return packets

if __name__ == "__main__":
    # Prueba unitaria del parser con un paquete simulado
    sample_packet = struct.pack(PACKET_FORMAT, 0xAA, 0x55, 12500, 2, 0.1, 0.05, 5.8, 150.4, 28.5, 0x1234)
    parsed = parse_telemetry_stream(sample_packet)
    print("Paquete Binario Decodificado Exitosamente:")
    print(parsed)
