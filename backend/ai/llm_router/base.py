from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

class BaseLLM(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass

    
@dataclass
class LLMResponse:
    provider: str
    text: str
    latency: float
    error: Optional[str] = None