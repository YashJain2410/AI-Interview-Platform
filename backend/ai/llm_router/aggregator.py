"""Deprecated single-adapter compatibility wrapper. Fan-out is intentionally disabled."""
from .base import BaseLLM, LLMResponse
from .settings import LLMConfigurationError


class LLMAggregator:
    def __init__(self, llms: list[BaseLLM]):
        if len(llms) != 1:
            raise LLMConfigurationError('Choose exactly one configured provider; multi-provider generation is disabled.')
        self.llm = llms[0]

    async def generate(self, prompt: str) -> LLMResponse:
        response = await self.llm.generate(prompt)
        if response.error or not response.text:
            raise RuntimeError('Selected provider failed. No fallback was attempted.')
        return response
