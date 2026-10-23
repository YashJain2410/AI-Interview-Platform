from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

class BaseLLM(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> "LLMResponse":
        pass


@dataclass
class LLMResponse:
    provider: str
    text: str
    latency: float
    error: Optional[str] = None
    model: Optional[str] = None
