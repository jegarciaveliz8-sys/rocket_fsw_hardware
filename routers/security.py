from fastapi import APIRouter, HTTPException
import hmac
import hashlib

router = APIRouter(prefix="/api/security", tags=["Cryptographic Uplink Security"])

SECRET_MISSION_KEY = b"ODYSSEY_SECURE_KEY_v1.3.0"

@router.post("/sign-command")
def sign_command_payload(payload: dict):
    """Genera una firma HMAC-SHA256 para comandos críticos de vuelo."""
    cmd = payload.get("command", "NOP")
    message = f"CMD:{cmd}".encode()
    signature = hmac.new(SECRET_MISSION_KEY, message, hashlib.sha256).hexdigest()
    return {
        "status": "success",
        "command": cmd,
        "hmac_signature": signature,
        "algorithm": "HMAC-SHA256"
    }

@router.post("/verify-command")
def verify_command_payload(payload: dict):
    """Valida la autenticidad de un comando recibido antes de inyectarlo al bus."""
    cmd = payload.get("command")
    received_sig = payload.get("signature")
    if not cmd or not received_sig:
        raise HTTPException(status_code=400, detail="Missing command or signature")
    
    expected_msg = f"CMD:{cmd}".encode()
    expected_sig = hmac.new(SECRET_MISSION_KEY, expected_msg, hashlib.sha256).hexdigest()
    
    is_valid = hmac.compare_digest(expected_sig, received_sig)
    return {
        "status": "success",
        "authenticated": is_valid,
        "message": "Uplink verified successfully" if is_valid else "Authentication failed: invalid signature"
    }
