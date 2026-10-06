# API entry point

`main.py` creates the FastAPI app and registers health, interview/audio sockets, and WebRTC signaling. `routers/interview.py` is a placeholder; no interview lifecycle HTTP API exists.

See [event contracts](../../docs/api.md) and [backend setup](../../docs/getting_started.md#backend-development). Imports eagerly initialize AI/audio dependencies, so startup can fail before health checks are available. CORS is permissive and no authentication is present.
