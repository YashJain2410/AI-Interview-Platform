import asyncio
from backend.realtime.audio_stream.tts.edge_tts import EdgeTTS

async def main():
    tts = EdgeTTS()
    audio = await tts.synthesize(
        "Hello Yash. This is a test of the AI interviewer voice."
    )

    with open("test.mp3", "wb") as f:
        f.write(audio)

    print("Saved_test.mp3")

asyncio.run(main())