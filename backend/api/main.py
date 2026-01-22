from fastapi import FastAPI
from realtime.websockets.router import router as interview_ws_router

app = FastAPI(title="AI Real-Time Voice Interview Platform")

app.include_router(interview_ws_router)

@app.get("/health")
async def health_check():
    return {"status" : "ok"}