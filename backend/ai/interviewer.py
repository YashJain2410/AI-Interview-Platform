from backend.ai.llm_router.router import LLMRouter
from backend.ai.prompts.loader import load_prompt
from backend.ai.llm_router.base import LLMResponse

class AIInterview:
    def __init__(self):
        self.llm_router = LLMRouter()

    async def ask_question(self, stage: str) -> str:
        prompt = load_prompt("interviewer.txt").format(stage = stage)
        response: LLMResponse = await self.llm_router.generate(prompt)
        return response.text
    
    async def ask_followup(self, answer: str) -> str:
        prompt = load_prompt("followup.txt").format(answer = answer)
        response: LLMResponse = await self.llm_router.generate(prompt)
        return response.text