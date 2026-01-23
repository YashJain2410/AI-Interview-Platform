import os

from .gemini_llm import GeminiLLM
from .huggingface_llm import HuggingFaceLLM

class LLMRouter:
    def __init__(self):
        provider = os.getenv("LLM_PROVIDER", "gemini")

        if provider == "gemini":
            self.llm = GeminiLLM()
        elif provider == "huggingface":
            self.llm = HuggingFaceLLM()
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
        
    async def generate(self, prompt: str) -> str:
        return await self.llm.generate(prompt)