import hmac
import hashlib

TC_KEY = b"ODYSSEY1_COMMAND_SECURE_KEY_2026"

def authenticate_and_parse_tc(command_hex: str) -> dict:
    """
    Verifica la autenticidad del telecomando de subida (TC) usando HMAC-SHA256
    y decodifica el código de instrucción operacional.
    """
    try:
        raw_data = bytes.fromhex(command_hex)
        if len(raw_data) < 36:
            return {"success": False, "error": "TC_FRAME_TOO_SHORT"}
            
        payload = raw_data[:-32]
        received_hmac = raw_data[-32:]
        
        calculated_hmac = hmac.new(TC_KEY, payload, hashlib.sha256).digest()
        if not hmac.compare_digest(received_hmac, calculated_hmac):
            return {"success": False, "error": "TC_AUTHENTICATION_FAILED_UNAUTHORIZED"}
            
        command_opcode = payload.decode('utf-8', errors='ignore')
        return {"success": True, "command": command_opcode, "clcw": "STATUS_ACCEPTED_EXECUTION_NOMINAL"}
    except Exception as e:
        return {"success": False, "error": str(e)}
