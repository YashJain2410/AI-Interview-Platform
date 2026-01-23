import os
import asyncio
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

from .base import LLMResponse

load_dotenv()

class GeminiLLM:
    def __init__(self):
        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY"),
            http_options={'api_version': 'v1'}
        ).aio
        
        self.model_id = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    async def generate(self, prompt: str) -> LLMResponse:
        start_time = time.perf_counter()        # More precise than time.time() for latency

        try:
            response = await self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=1.0,
                )
            )

            latency = time.perf_counter() - start_time

            return LLMResponse(
                provider="gemini",
                text = response.text,
                latency=latency
            )
        
        except Exception as e:
            latency = time.perf_counter() - start_time
            return LLMResponse(
                provider="gemini",
                text = "",
                latency=latency,
                error = str(e)
            )