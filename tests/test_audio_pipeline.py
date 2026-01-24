import asyncio
from backend.realtime.audio_stream.pipeline import AudioPipeline

async def main():
    with open("sample.wav", "rb") as f:
        audio_bytes = f.read()

    pipeline = AudioPipeline()
    response_audio = await pipeline.process_audio_chunck(audio_bytes)

    with open("response.mp3", "wb") as f:
        f.write(response_audio)
    
    print("Saved_response.mp3")

asyncio.run(main())