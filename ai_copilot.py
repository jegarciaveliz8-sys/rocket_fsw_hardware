import os
from google import genai

def ask_flight_director_ai(state_vector: dict, user_query: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return "⚠️ Error MCC: Variable de entorno GEMINI_API_KEY no configurada en el servidor."
        
    try:
        client = genai.Client(api_key=api_key)
        
        system_instructions = """
        Eres el Copiloto de Inteligencia Artificial del Centro de Control de Misión ODYSSEY-1 (NASA/ESA).
        Tu función es analizar la telemetría en tiempo real, evaluar riesgos ingenieriles de vuelo orbital y redactar procedimientos formales de recuperación o checklists de emergencia cuando se detecten anomalías o se te solicite.
        Responde siempre con rigor técnico de ingeniería aeroespacial de forma clara, directa y estructurada.
        """
        
        prompt = f"""
        {system_instructions}
        
        ==== VECTOR DE ESTADO EN TIEMPO REAL ====
        - Altitud: {state_vector.get('altitud_km', 'N/A')} km
        - Velocidad Orbital: {state_vector.get('velocidad_kms', 'N/A')} km/s
        - Estación DSN: {state_vector.get('estacion_dsn', 'N/A')} (Elevación: {state_vector.get('elevacion_dsn', 'N/A')}°)
        - Estado FDIR: {state_vector.get('estado_fdir', 'NOMINAL')}
        - Anomalía Detectada: {state_vector.get('falla_fdir', 'NONE')}
        - Estado de Subsistemas: {state_vector.get('matriz_subsistemas', {})}
        - Seguridad SDLS/CCSDS: {state_vector.get('sdls_status', 'VALID')}
        ========================================
        
        Consulta del Director de Vuelo: "{user_query}"
        
        Diagnóstico / Procedimiento de Respuesta:
        """
        
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=prompt
        )
        return response.text
        
    except Exception as e:
        return f"⚠️ Error en procesamiento del copiloto Gemini AI: {str(e)}"
