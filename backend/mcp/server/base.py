from abc import ABC, abstractmethod

class MCPServer(ABC):
    @abstractmethod
    async def get_context(self, **kwargs) -> dict:
        """
        Returns structured context to be injected into the LLM.
        """
        pass