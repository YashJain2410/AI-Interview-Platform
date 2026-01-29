from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.realtime.sessions.manager import SessionManager
from .connection import ConnectionManager
from backend.ai.interviewer import AIInterview
from backend.memory.session_memory import SessionMemory

router = APIRouter()
session_manager = SessionManager()
connection_manager = ConnectionManager()

@router.websocket("/ws/interview")
async def interview_socket(websocket: WebSocket):
    await websocket.accept()

    interviewer = AIInterview()
    session_memory = SessionMemory()
    last_ai_question = None

    try:
        init_payload = await websocket.receive_json()
        candidate_name = init_payload.get("candidate_name")

        session = session_manager.create_session(candidate_name)
        await connection_manager.connect(session.session_id, websocket)

        await websocket.send_json({
            "event" : "session_started",
            "session_id" : session.session_id,
            "stage" : session.stage
        })

        first_question = await interviewer.ask_question(stage=session.stage)
        last_ai_question = first_question

        await websocket.send_json({
            "event": "ai_question",
            "content": first_question
        })

        while True:
            data = await websocket.receive_json()
            candidate_answer = data.get("content")

            if not candidate_answer:
                continue

            ai_question, evaluation = await interviewer.ask_followup(
                answer=candidate_answer,
                stage = session.stage,
                previous_question = last_ai_question
            )

            if evaluation:
                session_memory.add_evaluation(evaluation)

            await websocket.send_json({
                "event" : "ai_question",
                "content" : ai_question
            })

            last_ai_question = ai_question

    except WebSocketDisconnect:
        connection_manager.disconnect(session.session_id)
        session_manager.end_session(session.session_id)