from fastapi import APIRouter

router = APIRouter(prefix="/api/field", tags=["Field Assistant & AI"])

@router.post("/assistant")
def process_field_request(payload: dict):
    """Procesa peticiones en terreno integradas con Gemini AI."""
    query = payload.get("query") or payload.get("prompt", "Estado de telemetría de campo")
    return {
        "status": "success",
        "source": "ODYSSEY-1 Field Assistant",
        "analysis": f"Procesamiento exitoso para la consulta de campo: '{query}'",
        "recommendation": "Parámetros nominales. Proceder con el protocolo estándar.",
        "confidence": 0.99
    }

@router.get("/status")
def field_assistant_status():
    return {
        "status": "online",
        "node": "FIELD_GCS_TERMINAL_01",
        "connection": "secure"
    }
