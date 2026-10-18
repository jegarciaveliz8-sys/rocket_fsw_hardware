import crccheck
import hashlib
import hmac

# Llave simétrica de seguridad para SDLS (Space Data Link Security)
SDLS_MASTER_KEY = b"ODYSSEY1_SECURE_KEY_2026"

def build_ccsds_frame(apid: int, data_payload: bytes) -> bytes:
    """
    Construye una trama CCSDS estándar (Packet Header + Payload + Security Trailer + CRC-16)
    """
    # 1. Cabecera Primaria CCSDS (6 bytes)
    pkt_id = (0 << 13) | (0 << 12) | (0 << 11) | (apid & 0x7FF)
    seq_ctrl = (3 << 14) | (1 & 0x3FFF)
    pkt_len = len(data_payload) + 5  # Incluyendo sufijo de seguridad parcial
    
    header = pkt_id.to_bytes(2, 'big') + seq_ctrl.to_bytes(2, 'big') + pkt_len.to_bytes(2, 'big')
    
    # 2. Seguridad SDLS (Autenticación HMAC-SHA256 truncada a 4 bytes)
    h = hmac.new(SDLS_MASTER_KEY, header + data_payload, hashlib.sha256).digest()[:4]
    
    frame_body = header + data_payload + h
    
    # 3. Código de Redundancia Cíclica CRC-16 CCSDS (2 bytes)
    crc = crccheck.crc.Crc16CcittFalse.calc(frame_body)
    full_frame = frame_body + crc.to_bytes(2, 'big')
    
    return full_frame

def verify_ccsds_frame(full_frame: bytes) -> dict:
    """
    Verifica la integridad de la trama, la autenticidad SDLS y el CRC-16.
    """
    if len(full_frame) < 12:
        return {"valid": False, "error": "FRAME_TOO_SHORT"}
        
    frame_body = full_frame[:-2]
    received_crc = int.from_bytes(full_frame[-2:], 'big')
    calculated_crc = crccheck.crc.Crc16CcittFalse.calc(frame_body)
    
    if received_crc != calculated_crc:
        return {"valid": False, "error": "CRC_MISMATCH"}
        
    # Extraer payload y etiqueta de seguridad
    # 6 bytes header + payload + 4 bytes HMAC
    payload_and_auth = frame_body[6:]
    received_hmac = payload_and_auth[-4:]
    actual_payload = payload_and_auth[:-4]
    header = frame_body[:6]
    
    expected_hmac = hmac.new(SDLS_MASTER_KEY, header + actual_payload, hashlib.sha256).digest()[:4]
    
    if not hmac.compare_digest(received_hmac, expected_hmac):
        return {"valid": False, "error": "SDLS_AUTHENTICATION_FAILURE"}
        
    return {"valid": True, "error": "NONE"}
