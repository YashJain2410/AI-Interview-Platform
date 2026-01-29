from backend.mcp.server.base import MCPServer
from backend.ai.evaluation.evaluator import InterviewEvaluator

class EvaluationContextServer(MCPServer):
    def __init__(self):
        self.evaluator = InterviewEvaluator()

    async def get_context(self, question: str | None = None, answer: str | None = None, **kwargs) -> dict:
        """Evaluates candidate's answer if question + answer exists"""

        if not question or not answer:
            return {}

        evaluation = await self.evaluator.evaluate_answer(question, answer)

        return {
            "evaluation" : evaluation.model_dump()
        }