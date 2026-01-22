from fastapi import FastAPI

app = FastAPI(title="AI Interview Platform")

@app.get("/health")
async def health_check():
    return {"status" : "ok"}