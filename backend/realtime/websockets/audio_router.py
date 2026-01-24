from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.realtime.audio_stream.pipeline import AudioPipeline

router = APIRouter()
pipeline = AudioPipeline()

@router.websocket("/ws/audio")
async def audio_socket(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            # Recieve raw audio bytes from client
            audio_bytes = await websocket.receive_bytes()

            # Process: STT -> AI -> TTS
            response_audio = await pipeline.process_audio_chunck(audio_bytes)

            # Send synthesized audio back
            await websocket.send_bytes(response_audio)

    except WebSocketDisconnect:
        print("Audio Websocket Disconnected")