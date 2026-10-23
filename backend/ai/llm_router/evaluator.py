from .router import LLMRouter

class LLMResponseEvaluator:
    """
    Uses an LLM to evaluate interview-quality of responses.
    """

    def __init__(self):
        self.judge_llm = LLMRouter()

    async def score(self, question: str, answer: str) -> float:
        prompt = f"""
You are evaluating an AI interviewer's question.

Question:
"{question}"

Proposed interview question:
"{answer}"

Score this question on a scale of 0 to 10 based on:
- Clarity
- Relevance to interview context
- Depth of assessment
- Professional tone
"""
        
        result = await self.judge_llm.generate(prompt)

        try:
            return float(result.text.strip())
        except Exception:
            return 0.0