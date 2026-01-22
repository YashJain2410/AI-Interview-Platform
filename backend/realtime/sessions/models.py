from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class InterviewStage(str, Enum):
    INTRO = "intro"
    HR = "hr"
    TECHNICAL = "technical"
    SYSTEM_DESIGN = "system_design"
    END = "end"

class InterviewMessage(BaseModel):
    role: str       # "ai" or "candidate"
    content: str
    timestamp: datetime

class InterviewSession(BaseModel):
    session_id: str
    candidate_name: Optional[str]
    stage: InterviewStage
    messages: List[InterviewMessage]
    started_at: datetime
