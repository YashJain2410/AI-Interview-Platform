# Real-time layer

`websockets/` handles text and an unfinished binary audio route. `webrtc/` handles SDP negotiation and media tracks. `audio_stream/` performs speech processing; `sessions/` stores text session state in memory.

Text and voice create separate interview instances. See [API contracts](../../docs/api.md), [voice flow](../../docs/realtime_pipeline.md), and [known limits](../../docs/project_status.md).
