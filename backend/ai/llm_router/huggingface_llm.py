"""Legacy adapter; selection remains owned by server configuration."""
from .base import LLMResponse
from .service import llm_service
from .settings import LLMConfigurationError, LLMSettings


class HuggingFaceLLM:
    async def generate(self, prompt: str) -> LLMResponse:
        settings = LLMSettings.from_env()
        if settings.provider != 'huggingface':
            raise LLMConfigurationError('This adapter requires LLM_PROVIDER=huggingface; automatic provider switching is disabled.')
        return await llm_service.generate(prompt)
