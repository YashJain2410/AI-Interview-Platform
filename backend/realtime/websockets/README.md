# WebSocket routes

`router.py` handles candidate initialization, questions, and answers on `/ws/interview`. `connection.py` tracks active text connections. `audio_router.py` declares `/ws/audio`, but calls a missing pipeline method.

See [API examples](../../../docs/api.md) for message order and shapes. Authentication, reconnection, and structured error events are not implemented.
