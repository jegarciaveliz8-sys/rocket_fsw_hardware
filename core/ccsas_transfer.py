import struct

def calculate_crc16(data: bytes) -> int:
    """Calcula CRC-16 CCITT para integridad de la trama física."""
    crc = 0xFFFF
    for b in data:
        crc ^= (b << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
            crc &= 0xFFFF
    return crc

def build_transfer_frame(scid: int, virtual_channel: int, frame_seq: int, space_packet: bytes) -> bytes:
    """
    Construye una Transfer Frame CCSDS (Primary Header: 4 bytes + Space Packet + CRC: 2 bytes).
    """
    # Header de 16 bits: Version (2) + SCID (10) + Virtual Channel (3) + OCF Flag (1)
    word1 = (0b00 << 14) | ((scid & 0x3FF) << 4) | ((virtual_channel & 0x07) << 1) | 0
    
    # Second Word: Frame Sequence Number (8 bits) + Reserved (8 bits)
    word2 = ((frame_seq & 0xFF) << 8) | 0x00
    
    transfer_header = struct.pack("!HH", word1, word2)
    frame_body = transfer_header + space_packet
    
    # Agregar CRC-16 al final
    crc = calculate_crc16(frame_body)
    return frame_body + struct.pack("!H", crc)
