import os
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    async def generate(self, prompt: str) -> str:
        """
        TEMPORARY mock LLM.
        We will replace this with OpenAI/Gemini later.
        """
        return f"[AI QUESTION GENERATED BASED ON]: {prompt[:80]}..."