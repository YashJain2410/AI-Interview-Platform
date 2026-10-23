"""Lightweight hosted API. Experimental local WebRTC stays opt-in."""
import os
from contextlib import asynccontextmanager

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
from backend.api.interviews import router

from backend.ai.llm_router.service import llm_service
from backend.ai.llm_router.settings import LLMConfigurationError, LLMSettings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Reuse TLS connections across interview turns; close them on shutdown.
    async with httpx.AsyncClient(follow_redirects=False) as client:
        llm_service.client = client
        try:
            yield
        finally:
            llm_service.client = None


app = FastAPI(title="Interview API", lifespan=lifespan)
origins = [x.strip().rstrip('/') for x in os.getenv(
    'ALLOWED_ORIGINS', 'http://localhost:5173,http://localhost:4173'
).split(',') if x.strip()]
app.state.allowed_origins = origins
app.add_middleware(CORSMiddleware, allow_origins=origins,
                   allow_methods=['GET', 'POST'], allow_headers=['Content-Type'])
app.include_router(router)

@app.get('/health')
async def health_check():
    try:
        settings = LLMSettings.from_env()
        ai = {'ai_configured': True, 'llm_provider': settings.provider, 'llm_model': settings.model}
    except LLMConfigurationError as exc:
        ai = {'ai_configured': False, 'configuration_error': str(exc)}
    return {'status': 'ok', **ai, 'llm_fallback_enabled': False, 'voice': 'browser', 'version': '2'}

if os.getenv('ENABLE_EXPERIMENTAL_AUDIO') == 'true':
    from backend.realtime.webrtc.router import router as audio_router
    app.include_router(audio_router)
