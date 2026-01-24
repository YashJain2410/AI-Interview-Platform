from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.realtime.sessions.manager import SessionManager
from .connection import ConnectionManager

router = APIRouter()
session_manager = SessionManager()
connection_manager = ConnectionManager()

@router.websocket("/ws/interview")
async def interview_socket(websocket: WebSocket):
    await websocket.accept()

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

        while True:
            data = await websocket.receive_json()

            await websocket.send_json({
                "event" : "candidate_message",
                "content" : data.get("content")
            })

    except WebSocketDisconnect:
        connection_manager.disconnect(session.session_id)
        session_manager.end_session(session.session_id)