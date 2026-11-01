import os
from fastapi import APIRouter
from google import genai
from google.genai import types

router = APIRouter(prefix="/api", tags=["AI Copilot & Commands"])

client = genai.Client()

@router.post("/ai/query")
def ai_query_endpoint(payload: dict):
    query_text = payload.get("query") or payload.get("prompt", "Estado general de misión")
    telemetry_context = payload.get("telemetry_context", {})
    
    mission_keywords = ["misión", "telemetría", "altitud", "velocidad", "propulsión", "fdir", "aviónica", "pitch", "roll", "yaw", "estado", "reporte", "ccsds", "hils"]
    is_mission_query = any(keyword in query_text.lower() for keyword in mission_keywords)

    if not is_mission_query and not ("estatus" in query_text.lower() or "diagnóstico" in query_text.lower()):
        system_instruction = (
            "Eres un asistente de IA amigable, culto, versátil y útil. "
            "Responde a cualquier pregunta general, de tecnología, ciencia, cocina, programación o charla cotidiana "
            "con total naturalidad, precisión y claridad, sin importar si hay datos de telemetría adjuntos en el entorno."
        )
        prompt = query_text
    else:
        system_instruction = (
            "Eres el AI Copilot oficial de la Estación de Control Terrestre (GCS) del ODYSSEY-1. "
            "Respondes con reportes técnicos de ingeniería aeroespacial claros, estructurados y profesionales. "
            "Utiliza la telemetría actual proporcionada para fundamentar tus respuestas y mantener un tono táctico."
        )
        prompt = (
            f"Pregunta del operador: \"{query_text}\"\n\n"
            f"Telemetría actual en vivo: {telemetry_context}\n\n"
            "Genera un informe técnico estructurado que incluya: "
            "1. Estatus de Parámetros Críticos, "
            "2. Evaluación de Riesgos y FDIR, y "
            "3. Recomendación Táctica."
        )

    try:
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7 if not is_mission_query else 0.3,
            ),
        )
        ai_response_text = response.text.replace("\n", "<br>")
    except Exception as e:
        ai_response_text = f"**[ADVERTENCIA FSW]** Error al conectar con el modelo de IA: {str(e)}"

    return {
        "status": "success",
        "response": ai_response_text,
        "confidence": 0.98
    }
