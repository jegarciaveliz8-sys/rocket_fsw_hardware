from fastapi import APIRouter
from pydantic import BaseModel
from routers import mission_path

router = APIRouter(prefix="/api/commands", tags=["Flight Commands"])

class CommandRequest(BaseModel):
    command: str

@router.post("/send")
async def execute_command(payload: CommandRequest):
    cmd = payload.command.upper()
    print(f"🕹️ [COMMAND GATEWAY] Orden recibida desde GCS Dashboard: {cmd}")
    
    response_action = "ACCEPTED"
    if cmd == "LAUNCH" or cmd == "TAKEOFF":
        mission_path.navigator.start_mission()
        msg = "Secuencia de lanzamiento iniciada. Dron ejecutando ruta autónoma en Sanarate."
    elif cmd == "ARM":
        msg = "Motores armados con éxito (Sistemas listos)."
    elif cmd == "RTL":
        mission_path.navigator.is_active = False
        msg = "Comando Return-To-Launch (RTL) activado. Retornando a base."
    elif cmd == "FTS_ABORT" or cmd == "FTS":
        mission_path.navigator.is_active = False
        msg = "¡ALERTA! Sistema de Terminación de Vuelo (FTS) ejecutado. Motores cortados."
    else:
        response_action = "UNKNOWN_COMMAND"
        msg = f"Comando '{cmd}' no reconocido por el FSW."
        
    return {
        "status": response_action,
        "command": cmd,
        "message": msg
    }
