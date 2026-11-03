import struct

def build_ccsas_packet(apid: int, sequence_count: int, data_payload: bytes) -> bytes:
    """
    Construye un paquete espacial CCSDS primario (Primary Header: 6 bytes).
    - Bits 0-2: Version Number (000)
    - Bit 3: Packet Type (0 = Telemetry, 1 = Command)
    - Bit 4: Secondary Header Flag (0 = No secondary header)
    - Bits 5-15: APID (Application Process Identifier)
    - Bits 16-17: Sequence Flags (11 = Unsegmented)
    - Bits 18-31: Packet Sequence Count (14 bits)
    - Bits 32-47: Packet Data Length - 1 (16 bits)
    """
    packet_type = 0  # Telemetría
    sec_hdr_flag = 0
    
    # Primer Word (16 bits): Version (3) + Type (1) + SecHdr (1) + APID (11)
    word1 = (0 << 13) | (packet_type << 12) | (sec_hdr_flag << 11) | (apid & 0x7FF)
    
    # Segundo Word (16 bits): Sequence Flags (2) + Sequence Count (14)
    seq_flags = 0b11
    word2 = (seq_flags << 14) | (sequence_count & 0x3FFF)
    
    # Tercer Word (16 bits): Data Length (Payload length - 1)
    data_len = len(data_payload) - 1
    if data_len < 0:
        data_len = 0
        
    primary_header = struct.pack("!HHH", word1, word2, data_len)
    return primary_header + data_payload

def parse_ccsas_packet(raw_bytes: bytes) -> dict:
    """Decodifica un paquete CCSDS en crudo y extrae sus campos y payload."""
    if len(raw_bytes) < 6:
        return {"error": "Paquete demasiado corto para cabecera CCSDS"}
        
    word1, word2, data_len = struct.unpack("!HHH", raw_bytes[:6])
    
    version = (word1 >> 13) & 0x07
    pkt_type = (word1 >> 12) & 0x01
    sec_hdr = (word1 >> 11) & 0x01
    apid = word1 & 0x7FF
    
    seq_flags = (word2 >> 14) & 0x03
    seq_count = word2 & 0x3FFF
    
    payload = raw_bytes[6:6 + data_len + 1]
    
    return {
        "version": version,
        "packet_type": "COMMAND" if pkt_type == 1 else "TELEMETRY",
        "secondary_header": bool(sec_hdr),
        "apid": apid,
        "sequence_flags": seq_flags,
        "sequence_count": seq_count,
        "data_length": data_len + 1,
        "payload_hex": payload.hex().upper(),
        "payload_raw": payload
    }

if __name__ == "__main__":
    # Prueba unitaria local
    sample_data = b"ALT:0.2726,VEL:-0.001"
    packet = build_ccsas_packet(apid=10, sequence_count=1, data_payload=sample_data)
    print("Paquete en Hex:", packet.hex().upper())
    print("Decodificado:", parse_ccsas_packet(packet))
