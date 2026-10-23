"""Compatibility entry point for interview and evaluation pipelines."""
from .base import LLMResponse
from .service import llm_service


class LLMRouter:
    async def generate(self, prompt: str) -> LLMResponse:
        return await llm_service.generate(prompt)
