import logging
from google import genai
from google.genai import types

logger = logging.getLogger("ODYSSEY-FDIR-AI")

class AutonomousFDIRHandler:
    def __init__(self, api_key: str = None):
        self.client = genai.Client(api_key=api_key) if api_key else genai.Client()

    async def evaluate_and_mitigate(self, telemetry_packet: dict) -> dict:
        prompt = f"""
        Analyze the following spacecraft telemetry packet and determine if an autonomous recovery action is required.
        Telemetry: {telemetry_packet}
        
        Provide a JSON response with:
        - "action_required": true/false
        - "command_code": string identifier of the correction command (e.g., "RECONFIG_TVC", "SAFE_MODE", "NONE")
        - "reason": brief explanation
        """
        
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
        )
        
        return response.text
