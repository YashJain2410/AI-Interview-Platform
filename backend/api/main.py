from fastapi import FastAPI
from backend.realtime.websockets.router import router as interview_ws_router
from backend.realtime.websockets.audio_router import router as audio_ws_router

app = FastAPI(title="AI Real-Time Voice Interview Platform")

app.include_router(interview_ws_router)
app.include_router(audio_ws_router)

@app.get("/health")
async def health_check():
    return {"status" : "ok"}