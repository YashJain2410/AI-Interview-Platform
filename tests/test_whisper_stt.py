import asyncio
import tempfile
from backend.realtime.audio_stream.stt.whisper_stt import WhisperSTT

async def main():
    # with open("debug_processed_1769489104.wav", "rb") as f:
    #     audio_bytes = f.read()

    stt = WhisperSTT()
    text = await stt.transcribe(r"C:\Users\HP\DATAA\YASH\Projects\Interview_Agent\debug_processed_1769489104.wav")
    print("Transcribed text: ", text)

asyncio.run(main())