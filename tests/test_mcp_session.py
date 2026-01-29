import asyncio
from backend.ai.interviewer import AIInterview
from backend.realtime.sessions.manager import SessionManager

async def test_session_flow():
    session_mgr = SessionManager()
    interviewer = AIInterview()

    session_id = session_mgr.create_session()
    print("Session:", session_id)

    q1 = await interviewer.ask_question(stage="technical")
    session_mgr.update_last_ai_question(session_id, q1)