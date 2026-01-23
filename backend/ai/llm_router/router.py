from .gemini_llm import GeminiLLM
from .huggingface_llm import HuggingFaceLLM
from .aggregator import LLMAggregator
from .base import LLMResponse

class LLMRouter:
    def __init__(self):
        self.aggregator = LLMAggregator([
            GeminiLLM(),
            HuggingFaceLLM()
        ])
        
    async def generate(self, prompt: str) -> LLMResponse:
        return await self.aggregator.generate(prompt)