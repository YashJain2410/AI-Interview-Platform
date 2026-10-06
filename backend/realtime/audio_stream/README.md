# Speech processing

`pipeline.py` buffers PCM audio, detects turn endings, transcribes with Whisper, generates a follow-up, and synthesizes speech with Edge TTS. ffmpeg converts speech output to 48 kHz mono PCM16.

Recognition and synthesis process complete utterances. TTS input, timestamps, buffer limits, and cleanup have unresolved defects. See [voice pipeline](../../../docs/realtime_pipeline.md) before attempting full voice operation.
