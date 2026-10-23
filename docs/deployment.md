# Vercel frontend + Render backend

The hosted API uses lightweight HTTP calls to one explicitly selected provider and model.
Google Gemini is the default. Automatic provider/model fallback and retries are disabled.
See [model configuration](model_configuration.md) for provider options and tuning.
The browser uses one WebSocket for questions, answers, and the final report. Browser speech
recognition dictates into the answer editor; browser speech synthesis reads questions aloud.
The original Whisper/WebRTC experiment remains separate and disabled by default.

## Render

- Repository root, Python 3.12 (`.python-version`).
- Build: `pip install -r requirements.txt`
- Start: `uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT --workers 1`
- Health check: `/health`
- Secret environment: `GEMINI_API_KEY` for the default Google provider.
- `LLM_PROVIDER=google` and `LLM_MODEL=gemini-3.8-flash`.
- `ALLOWED_ORIGINS=https://<production-frontend>.vercel.app` (comma-separated exact origins).
- `render.yaml` records the service configuration without secrets.

## Vercel

Import only `frontend/web` with the Vite preset. Build with `npm run build`, install with
`npm ci`, and serve `dist`. The committed `vercel.json` handles React Router deep links.
Set `VITE_API_URL=https://<service>.onrender.com` and optionally
`VITE_WS_URL=wss://<service>.onrender.com`, then rebuild. These are public URLs; never
put provider credentials into `VITE_*` variables.

## Verification

Run `npm run build --prefix frontend/web` and
`.venv/bin/python -m unittest discover -s tests/deployment -v`.
On the public frontend, complete setup → first AI question → answer → answer-aware
follow-up → End interview → real feedback → history → refresh a report deep link.
Check PDF/DOCX/TXT ingestion and microphone dictation in Chrome over HTTPS.

## Operating limits

Render Free sleeps on idle, so the frontend waits up to two minutes while waking the API.
Active interviews are process-local and end on restart or disconnect. Reports and profile
preferences are saved in this browser's local storage, not in a cloud account. The API
has bounded sessions, input sizes, provider deadlines, exact CORS/WebSocket origins, and
basic per-IP session limits; it is a public practice app, without user accounts or durable
server-side history. Uploaded files are extracted in memory; extracted context and answers
are sent to the configured AI provider. Browser dictation may use the browser vendor's
speech service. Scanned PDFs require OCR before upload.

Provider failures are visible errors and never substituted with canned interview answers.
`/health` reports configuration presence, not provider quota or availability. Test a real
interview after changes to credentials or models. Free hosting and external AI availability
cannot provide an uptime guarantee.

## Private files

`docs/competitive-research.md`, `docs/platform-explained.md`, `.env`, and generated
candidate data are ignored by Git. Keep secrets only in the backend environment.
