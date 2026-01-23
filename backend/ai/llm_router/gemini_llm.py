import os
import asyncio
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class GeminiLLM:
    def __init__(self):
        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY"),
            http_options={'api_version': 'v1'}
        )
        
        self.model_id = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")

    async def generate(self, prompt: str) -> str:
        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model=self.model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=1.0,
            )
        )
        return response.text