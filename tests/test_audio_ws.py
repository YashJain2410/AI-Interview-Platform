import asyncio
import websockets

async def main():
    uri = "ws://127.0.0.1:8000/ws/audio"

    async with websockets.connect(uri) as websocket:
        with open("sample.wav", "rb") as f:
            audio_bytes = f.read()

        await websocket.send(audio_bytes)

        response = await websocket.recv()

        with open("ws_response.mp3", "wb") as f:
            f.write(response)

        print("Saved ws_response.mp3")

asyncio.run(main())