import asyncio
import tempfile
from backend.realtime.audio_stream.stt.whisper_stt import WhisperSTT

async def main():
    with open("sample.wav", "rb") as f:
        audio_bytes = f.read()

    stt = WhisperSTT()
    text = await stt.transcribe(audio_bytes)
    print("Transcribed text: ", text)

asyncio.run(main())