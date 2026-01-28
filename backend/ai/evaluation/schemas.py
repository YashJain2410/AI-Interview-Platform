from pydantic import BaseModel
from typing import Dict

class ScoreBreakdown(BaseModel):
    technical_correctness: int
    depth_of_understanding: int
    communication: int
    confidence: int

class EvaluationResult(BaseModel):
    scores: ScoreBreakdown
    total_score: int
    strengths: list[str]
    weaknesses: list[str]
    improvement_suggestions: list[str]