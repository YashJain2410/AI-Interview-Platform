"""String-returning compatibility client backed by the configured provider."""
from .service import llm_service


class LLMClient:
    async def generate(self, prompt: str) -> str:
        return (await llm_service.generate(prompt)).text
