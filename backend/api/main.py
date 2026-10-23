"""Lightweight hosted API. Experimental local WebRTC stays opt-in."""
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
from backend.api.interviews import router

app = FastAPI(title="Interview API")
origins = [x.strip().rstrip('/') for x in os.getenv(
    'ALLOWED_ORIGINS', 'http://localhost:5173,http://localhost:4173'
).split(',') if x.strip()]
app.state.allowed_origins = origins
app.add_middleware(CORSMiddleware, allow_origins=origins,
                   allow_methods=['GET', 'POST'], allow_headers=['Content-Type'])
app.include_router(router)

@app.get('/health')
async def health_check():
    return {'status': 'ok', 'ai_configured': bool(os.getenv('GEMINI_API_KEY') or os.getenv('HF_API_TOKEN')),
            'voice': 'browser', 'version': '2'}

if os.getenv('ENABLE_EXPERIMENTAL_AUDIO') == 'true':
    from backend.realtime.webrtc.router import router as audio_router
    app.include_router(audio_router)
