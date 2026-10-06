# Voice pipeline

The voice path combines browser media with utterance-based speech processing. Audio transport is continuous; transcription and synthesis operate on complete turns.

```mermaid
flowchart LR
    Mic[Browser microphone] --> RTC[WebRTC input]
    RTC --> PCM[48 kHz mono PCM16]
    PCM --> VAD[Energy threshold + silence detection]
    VAD --> WAV[16 kHz WAV utterance]
    WAV --> STT[Whisper transcription]
    STT --> AI[AI follow-up]
    AI --> TTS[Edge TTS MP3]
    TTS --> Convert[ffmpeg → 48 kHz PCM16]
    Convert --> Output[WebRTC playback]
```

## Turn handling

The pipeline uses 20 ms chunks at 48 kHz. Average absolute sample energy above `500` marks speech; 25 silent chunks end a turn. Utterances shorter than one second are skipped. These are fixed heuristics, not validated noise-robust VAD settings.

Whisper transcribes a temporary WAV after the turn ends. Edge TTS generates an MP3, then ffmpeg converts it to playback PCM. There are no partial transcripts or token-by-token speech generation.

## Known integration limits

- Follow-up generation returns `(question, evaluation)`; the pipeline passes that tuple to TTS instead of question text.
- The outgoing track sets an invalid string audio time base.
- Queues and initial-silence accumulation are unbounded; peer cleanup does not fully stop pipeline workers.
- Voice and text sessions, transcripts, and evaluation are separate.
- The browser uses STUN only, with no TURN configuration or complete ICE candidate exchange.
- Debug audio and transcripts are written/logged; retention and deletion are not enforced.

The binary WebSocket route also invokes a missing method. See [status](project_status.md) before using voice in a demonstration, and [deployment](deployment.md) for public-network requirements.
