# Interview Web

The production-ready React frontend for the AI voice interview platform. It includes the full candidate journey: overview, interview setup, live voice room, reports, history, and preferences.

## Run locally

```bash
npm install
cp .env.example .env
npm run dev
```

The frontend expects the FastAPI service at `http://localhost:8000` by default. Use `VITE_API_URL` and `VITE_WS_URL` to point at a deployed backend.

## Backend integration

- `POST /webrtc/offer` for live microphone/audio negotiation
- `WS /ws/interview` for interview questions and text answers
- `WS /ws/audio` is supported by the backend and can be added as an alternate streaming transport

When the backend is unavailable, the live room enters a clearly labelled demo mode so the full interface remains reviewable.

## Deploy on Vercel

Set the project root to `frontend/web`, use `npm run build`, and publish `dist`. Add the production API and WebSocket URLs as Vercel environment variables.
