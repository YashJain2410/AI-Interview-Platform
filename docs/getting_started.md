# Getting started

Run commands from the repository root unless a step changes directories.

## Frontend demo

Use a current Node.js LTS release supported by the locked Vite version.

```bash
cd frontend/web
npm ci
cp .env.example .env
npm run dev
```

Open the URL Vite prints. With no backend, the live room can use fallback demo responses. Reports and analytics are sample data even when a backend is connected.

```bash
npm run build
npm run preview
```

The build outputs `frontend/web/dist/`. Preview serves the built frontend locally.

## Backend development

**Setup is currently exploratory, not a verified clean-install recipe.** Root `requirements.txt` contains only a small FastAPI dependency set; it is not a complete backend manifest. There is no backend bootstrap script or container configuration.

Use Python 3.11 as a starting point, a virtual environment, ffmpeg on `PATH`, and network access for models/providers. Dependency compatibility has not been established across platforms.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
cp .env.example .env
```

Install the root requirements and additional imported packages into that environment:

```bash
python -m pip install -r requirements.txt
python -m pip install aiortc av numpy soundfile librosa resampy openai-whisper edge-tts google-genai huggingface-hub sentence-transformers faiss-cpu langchain-text-splitters websockets
ffmpeg -version
```

These additional packages are unpinned; this is a development starting point, not a reproducible release environment. Whisper also requires its model/runtime dependencies. First model loads may download files and take time.

Fill `GEMINI_API_KEY` and `HF_API_TOKEN` in `.env`. Model overrides are optional. Provider access depends on your account, model availability, and quotas.

Create non-empty synthetic text files at `data/resumes/resume.txt` and `data/job_descriptions/jd.txt`. Use enough text for at least three chunks in each index. Generate the indexes before starting the server:

```bash
python - <<'PYCODE'
from pathlib import Path
from backend.ai.rag.ingest import RAGIngestor

Path("data/embeddings").mkdir(parents=True, exist_ok=True)
ingestor = RAGIngestor()
ingestor.ingest_file(Path("data/resumes/resume.txt"), "resume")
ingestor.ingest_file(Path("data/job_descriptions/jd.txt"), "jd")
PYCODE
```

Start from the repository root so relative prompt/index paths resolve:

```bash
python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000
```

Model loading and audio initialization occur during import, so startup can fail before `/health` is available. The global audio pipeline also creates an asyncio task during initialization; import-based tooling may encounter a missing running event loop. Backend startup and full voice operation are not certified by this guide.

If startup succeeds, check `http://localhost:8000/health` and `/docs`; then use the [text event contract](api.md#text-interview).

## Configuration

| Variable | Used by | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | Gemini client | Server-side provider credential |
| `GEMINI_MODEL` | Gemini client | Optional model override |
| `HF_API_TOKEN` | Hugging Face client | Server-side provider credential |
| `HF_MODEL` | Hugging Face client | Optional model override |
| `VITE_API_URL` | Frontend | HTTP backend origin |
| `VITE_WS_URL` | Frontend | WebSocket backend origin |

The root `.env` supplies backend credentials. `frontend/web/.env` supplies browser configuration. Vite variables are public build-time values; never put secrets in them. FAISS paths are currently hardcoded under `data/embeddings/`.

## Troubleshooting

| Symptom | Check |
|---|---|
| Missing Python module | The dependency manifests are incomplete; inspect the imports and packages above. |
| Missing `resume.pkl` / `jd.pkl` | Generate both indexes from the repository root. |
| Model initialization fails | Network access, model cache permissions, provider keys, and memory. |
| Frontend shows demo answers | Backend/socket availability; demo responses are not provider results. |
| Microphone cannot start | Browser permission and HTTPS or localhost; voice also has known code defects. |
| Audio never plays | Known TTS tuple/timestamp defects; see [voice guide](realtime_pipeline.md). |
| Deep link returns 404 on hosting | Configure SPA rewrites to `index.html`. |
