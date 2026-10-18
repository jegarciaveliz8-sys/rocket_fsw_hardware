import struct

# Formato binario: [ID Misión (8 chars), Secuencia (H), Altitud (f), Velocidad (f), Aceleración (f)]
PACKET_FORMAT = "8s H f f f"

def pack_telemetry(mission_id: str, seq: int, alt: float, vel: float, accel: float) -> bytes:
    return struct.pack(PACKET_FORMAT, mission_id.encode('utf-8'), seq, alt, vel, accel)

def unpack_telemetry(data: bytes):
    unpacked = struct.unpack(PACKET_FORMAT, data)
    return {
        "mission_id": unpacked[0].decode('utf-8').strip('\x00'),
        "seq": unpacked[1],
        "altitude": unpacked[2],
        "velocity": unpacked[3],
        "acceleration": unpacked[4]
    }
