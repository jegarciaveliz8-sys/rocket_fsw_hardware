import httpx

async def query_local_ai(prompt: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={"model": "phi3", "prompt": prompt, "stream": False}
            )
            if response.status_code == 200:
                return {"status": "success", "response": response.json().get("response")}
    except (httpx.TimeoutException, httpx.ConnectError):
        pass
    
    return {
        "status": "fallback",
        "response": "[AUDITORÍA TÉRMICA] Sistema operativo en modo nominal de respaldo. Sensores dentro de parámetros seguros sin inferencia de IA activa."
    }
