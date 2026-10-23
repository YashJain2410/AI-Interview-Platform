"""Legacy adapter; selection remains owned by server configuration."""
from .base import LLMResponse
from .service import llm_service
from .settings import LLMConfigurationError, LLMSettings


class GeminiLLM:
    async def generate(self, prompt: str) -> LLMResponse:
        settings = LLMSettings.from_env()
        if settings.provider != 'google':
            raise LLMConfigurationError('This adapter requires LLM_PROVIDER=google; automatic provider switching is disabled.')
        return await llm_service.generate(prompt)
