import crccheck

def build_ccsds_frame(apid: int, data_payload: bytes) -> bytes:
    # Cabecera Primaria CCSDS simplificada (6 bytes)
    # Packet ID (Version 3 bits, Type 1 bit, Secondary Header 1 bit, APID 11 bits)
    pkt_id = (0 << 13) | (0 << 12) | (0 << 11) | (apid & 0x7FF)
    
    # Packet Sequence Control (Sequence Flags 2 bits, Packet Count 14 bits)
    seq_ctrl = (3 << 14) | (1 & 0x3FFF)
    
    pkt_len = len(data_payload) - 1 if len(data_payload) > 0 else 0
    
    header = pkt_id.to_bytes(2, 'big') + seq_ctrl.to_bytes(2, 'big') + pkt_len.to_bytes(2, 'big')
    frame = header + data_payload
    
    # Cálculo CRC-16 CCSDS
    crc = crccheck.crc.Crc16CcittFalse.calc(frame)
    return frame + crc.to_bytes(2, 'big')

def verify_ccsds_frame(full_frame: bytes) -> bool:
    if len(full_frame) < 8:
        return False
    payload_and_header = full_frame[:-2]
    received_crc = int.from_bytes(full_frame[-2:], 'big')
    calculated_crc = crccheck.crc.Crc16CcittFalse.calc(payload_and_header)
    return received_crc == calculated_crc
