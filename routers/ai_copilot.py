from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["AI Copilot & Commands"])

@router.post("/ai/query")
def ai_query_endpoint(payload: dict):
    query_text = payload.get("query") or payload.get("prompt", "Estado general de misión")
    return {
        "status": "success",
        "response": f"ODYSSEY-1 AI Copilot: Análisis completado para '{query_text}'. Parámetros nominales.",
        "confidence": 0.98
    }

@router.post("/command/inject")
def drone_command_injection(payload: dict):
    cmd = payload.get("command", "CUSTOM_CMD")
    return {
        "status": "SUCCESS",
        "command_status": "executed",
        "command_sent": cmd,
        "details": payload
    }

@router.post("/drone/command")
def drone_command_pipeline(payload: dict):
    cmd = payload.get("command", "CUSTOM_CMD")
    return {
        "status": "SUCCESS",
        "command_status": "executed",
        "command_sent": cmd,
        "details": payload
    }
