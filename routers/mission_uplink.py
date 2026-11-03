from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

try:
    from core.security_hmac import verify_command_signature
    from core.ccsas_parser import build_ccsas_packet, parse_ccsas_packet
    from scripts.db_logger import log_fdir_event
    from routers.mission_api import fsw_state
except ImportError:
    def verify_command_signature(*args, **kwargs): return True
    def log_fdir_event(*args): pass
    fsw_state = {"status": "NOMINAL", "battery_pct": 100.0}

router = APIRouter(prefix="/api/mission", tags=["Mission Uplink & CCSDS"])

class UplinkCommandRequest(BaseModel):
    command: str
    timestamp: int
    counter: int
    signature: str

@router.post("/uplink")
async def send_secure_uplink(req: UplinkCommandRequest):
    """
    Recibe un comando uplink, verifica la firma HMAC y el contador,
    y empaqueta la instrucción bajo el estándar CCSDS.
    """
    # 1. Validación de seguridad HMAC & Anti-Replay
    is_authenticated = verify_command_signature(
        req.command, req.timestamp, req.counter, req.signature
    )
    
    if not is_authenticated:
        log_fdir_event("SECURITY_BREACH", "CRITICAL", f"Firma HMAC inválida para comando: {req.command}")
        raise HTTPException(status_code=401, detail="UPLINK REJECTED: Invalid HMAC signature or timestamp drift.")

    # 2. Empaquetado bajo estándar CCSDS Space Packet Protocol
    payload_bytes = req.command.encode('utf-8')
    ccsas_pkt = build_ccsas_packet(apid=42, sequence_count=req.counter, data_payload=payload_bytes)
    parsed_pkt = parse_ccsas_packet(ccsas_pkt)

    # 3. Ejecución del comando en el RTOS de la FSW
    cmd_upper = req.command.upper()
    if "ABORT" in cmd_upper:
        fsw_state["status"] = "ABORTED"
        log_fdir_event("MISSION_ABORT", "ACTIVE", "Aborto seguro ejecutado vía HMAC uplink.")
    elif "RESET" in cmd_upper:
        fsw_state["status"] = "NOMINAL"
        log_fdir_event("SYSTEM_RESET", "RESOLVED", "Reinicio de subsistemas ordenado por GCS.")

    return {
        "status": "SUCCESS",
        "message": f"Comando autenticado y empaquetado bajo CCSDS en Sanarate.",
        "ccsas_packet_hex": ccsas_pkt.hex().upper(),
        "parsed_packet": parsed_pkt,
        "fsw_status": fsw_state.get("status")
    }
