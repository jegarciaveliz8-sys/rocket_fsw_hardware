import os
from fastapi import APIRouter
from pydantic import BaseModel

try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

try:
    from routers.mission_api import fsw_state
except ImportError:
    fsw_state = {
        "time": 0,
        "altitude": 0.0,
        "velocity": 0.0,
        "chamber_pressure": 15.4,
        "battery_pct": 100.0,
        "lat": 14.7883,
        "lon": -90.1988,
        "status": "STANDBY / READY"
    }

router = APIRouter(prefix="/api/ai", tags=["AI Copilot"])

class AIPromptRequest(BaseModel):
    prompt: str

@router.post("/diagnose")
async def diagnose_flight(req: AIPromptRequest):
    query = req.prompt.strip()

    current_alt = fsw_state.get("altitude", 0.0)
    current_vel = fsw_state.get("velocity", 0.0)
    current_bat = fsw_state.get("battery_pct", 100.0)
    current_status = fsw_state.get("status", "NOMINAL")
    current_press = fsw_state.get("chamber_pressure", 15.4)
    current_lat = fsw_state.get("lat", 14.7883)
    current_lon = fsw_state.get("lon", -90.1988)

    api_key = os.environ.get("GEMINI_API_KEY")

    if api_key and HAS_GENAI:
        try:
            client = genai.Client(api_key=api_key)
            
            system_instruction = (
                "Eres el Copiloto AI del Centro de Control de Misión ODYSSEY-1 en Sanarate. "
                "Tienes autonomía e inteligencia total. Puedes responder con fluidez, profundidad y precisión "
                "sobre cualquier tema del mundo (programación, arquitectura de software, física, matemáticas, "
                "historia, recomendaciones o cultura general). "
                "Cuando el usuario consulte sobre el estado de la misión, el vehículo, la telemetría o los subsistemas, "
                "integra dinámicamente los datos en tiempo real. Para cualquier otra consulta general, responde como "
                "un copiloto brillante y sin restricciones temáticas."
            )

            context_prompt = (
                f"[Telemetría en Vivo de ODYSSEY-1]\n"
                f"- Estado: {current_status}\n"
                f"- Coordenadas: Lat {current_lat}, Lon {current_lon}\n"
                f"- Altitud: {current_alt} m\n"
                f"- Velocidad: {current_vel} m/s\n"
                f"- Batería: {current_bat} %\n"
                f"- Presión de Cámara: {current_press} MPa\n\n"
                f"Consulta del Usuario: {query}"
            )

            # Usando un modelo confirmado de tu listado oficial
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=context_prompt,
                config={
                    "system_instruction": system_instruction
                }
            )
            
            if response and response.text:
                return {
                    "status": "SUCCESS",
                    "response": response.text.strip()
                }
        except Exception as e:
            print(f"[Gemini Error Detallado]: {e}")

    return {
        "status": "SUCCESS",
        "response": (
            f"🧠 **Copiloto AI (Modo Local):** Recibido: \"{query}\".\n\n"
            f"📍 **Telemetría Actual:** Altitud: {current_alt} m | Velocidad: {current_vel} m/s | Batería: {current_bat}% | Estado: {current_status}\n\n"
            f"*(Asegúrate de que la variable `GEMINI_API_KEY` esté configurada correctamente en el archivo .env)*."
        )
    }
