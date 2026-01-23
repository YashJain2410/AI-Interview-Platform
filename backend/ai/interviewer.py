from .llm_router.router import LLMRouter
from .prompts.loader import load_prompt

class AIInterview:
    def __init__(self):
        self.llm_router = LLMRouter()

    async def ask_question(self, stage: str) -> str:
        prompt = load_prompt("interviewer.txt").format(stage = stage)
        return await self.llm_router.generate(prompt)
    
    async def ask_followup(self, answer: str) -> str:
        prompt = load_prompt("followup.txt").format(answer = answer)
        return await self.llm_router.generate(prompt)