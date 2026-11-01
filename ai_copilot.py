import os
from google import genai
from google.genai import types

client = genai.Client()

def get_ai_response(query: str, telemetry: dict) -> str:
    # --- CÓDIGO ANTERIOR (Comentado para referencia) ---
    # return (
    #     f"**[INFORME TÉCNICO FSW - ODYSSEY-1]**<br>"
    #     f"**Consulta Operador:** \"{query}\"<br><br>"
    #     "1. **Estatus de Parámetros Críticos**:<br>"
    #     "- Altitud: Nominal (~398-402 km, EKF estable).<br>"
    #     "- Presión de Cámara ($Pc$): 15.4 MPa (Envolvente nominal).<br>"
    #     "- Velocidad orbital: ~7669 m/s.<br><br>"
    #     "2. **Evaluación de Riesgos y FDIR**:<br>"
    #     "- Sin anomalías térmicas en aviónica.<br>"
    #     "- Actitud orientada (Pitch: 3.92°, Yaw: 0°, Roll: 161°). Sin derivas angulares críticas.<br>"
    #     "- Enlaces DSN (Madrid DSS-63) sincronizados sin pérdida de tramas CCSDS.<br><br>"
    #     "3. **Recomendación Táctica**:<br>"
    #     "- Mantener secuencia actual en modo **STANDBY**.<br>"
    #     "- Autorizado el monitoreo continuo de telemetría HIL."
    # )
    # --------------------------------------------------

    # Nueva lógica dual adaptativa (Preguntas de misión vs Preguntas generales)
    mission_keywords = ["misión", "telemetría", "altitud", "velocidad", "propulsión", "fdir", "aviónica", "pitch", "roll", "yaw", "estado", "reporte", "ccsds", "hils"]
    is_mission_query = any(keyword in query.lower() for keyword in mission_keywords)

    if not is_mission_query and not ("estatus" in query.lower() or "diagnóstico" in query.lower()):
        system_instruction = (
            "Eres un asistente de IA amigable, culto, versátil y útil. "
            "Responde a cualquier pregunta general, de tecnología, ciencia, cocina, programación o charla cotidiana "
            "con total naturalidad, precisión y claridad, sin importar si hay datos de telemetría adjuntos."
        )
        prompt = query
    else:
        system_instruction = (
            "Eres el AI Copilot oficial de la Estación de Control Terrestre (GCS) del ODYSSEY-1. "
            "Respondes con reportes técnicos de ingeniería aeroespacial claros, estructurados y profesionales. "
            "Utiliza la telemetría actual proporcionada para fundamentar tus respuestas y mantener un tono táctico."
        )
        prompt = (
            f"Pregunta del operador: \"{query}\"\n\n"
            f"Telemetría actual en vivo: {telemetry}\n\n"
            "Genera un informe técnico estructurado que incluya: "
            "1. Estatus de Parámetros Críticos, "
            "2. Evaluación de Riesgos y FDIR, y "
            "3. Recomendación Táctica."
        )

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7 if not is_mission_query else 0.3,
            ),
        )
        ai_response_text = response.text.replace("\n", "<br>")
    except Exception as e:
        ai_response_text = f"**[ADVERTENCIA FSW]** Error al conectar con el modelo de IA: {str(e)}"

    return ai_response_text
