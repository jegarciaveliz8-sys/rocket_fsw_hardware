import os
from google import genai

def ask_flight_director_ai(state_vector, user_query):
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return "Error: GEMINI_API_KEY no configurada en el servidor."
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    Eres el Copiloto Experto de Misión para el Centro de Control ODYSSEY-1.
    Vector de Estado Actual del Cohete:
    - Posición/Altitud/Velocidad: {state_vector}
    
    Responde a la consulta técnica del Director de Vuelo con rigor ingenieril aeroespacial:
    Consulta: {user_query}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    return response.text
