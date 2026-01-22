from fastapi import FastAPI
from api.routers import interview

app = FastAPI(title="AI Interview Platform")

app.include_router(interview.router)