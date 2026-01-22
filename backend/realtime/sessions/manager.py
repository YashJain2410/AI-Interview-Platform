import uuid
from datetime import datetime
from typing import Dict, Optional

from .models import InterviewSession, InterviewStage

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, InterviewSession] = {}

    def create_session(self, candidate_name: Optional[str] = None) -> InterviewSession:
        session_id = str(uuid.uuid4())

        session = InterviewSession(
            session_id = session_id,
            candidate_name=candidate_name,
            stage = InterviewStage.INTRO,
            messages=[],
            started_at=datetime.utcnow()
        )

        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        return self.sessions.get(session_id)
    
    def end_session(self, session_id: str):
        self.sessions.pop(session_id, None)