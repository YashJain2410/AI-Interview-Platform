from backend.ai.llm_router.router import LLMRouter
from backend.ai.evaluation.rubric import INTERVIEW_RUBRIC
from backend.ai.evaluation.schemas import EvaluationResult

class InterviewEvaluator:
    def __init__(self):
        self.llm = LLMRouter()

    async def evaluate_answer(self, question: str, answer: str) -> EvaluationResult:
        rubric_text = "\n".join(
            f"- {k} (max {v['max_score']}): {v['description']}"
            for k, v in INTERVIEW_RUBRIC.items()
        )

        prompt = f"""
You are an expert technical interviewer. 
Evaluate the candidate's answer strictly using the rubric below.

Rubric: 
{rubric_text}

Question:
"{question}"

Candidate's Answer:
"{answer}"

Return ONLY valid JSON in this format:
{{
    "scores": {{
        "technical_correctness": int,
        "depth_of_understanding": int,
        "communication": int,
        "confidence": int
    }},
    "total_score": int,
    "strengths": [string],
    "weaknesses": [string],
    "improvement_suggestions": [string]
}}
"""
        
        response = await self.llm.generate(prompt)
        return EvaluationResult.model_validate_json(response.text)