from fastapi import FastAPI
from backend.realtime.websockets.router import router as interview_ws_router
from backend.realtime.websockets.audio_router import router as audio_ws_router
from backend.realtime.webrtc.router import router as webrtc_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Real-Time Voice Interview Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interview_ws_router)
app.include_router(audio_ws_router)
app.include_router(webrtc_router)

@app.get("/health")
async def health_check():
    return {"status" : "ok"}