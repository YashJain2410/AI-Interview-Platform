import asyncio
import websockets
import json

async def test_ws():
    uri = "ws://localhost:8000/ws/interview"

    async with websockets.connect(uri) as ws:
        # Send init payload
        await ws.send(json.dumps({
            "candidate_name": "Yash"
        }))

        # Receive session_started
        msg = await ws.recv()
        print("SERVER:", msg)

        # Receive first AI question
        msg = await ws.recv()
        print("AI:", msg)

        # Send candidate answer
        await ws.send(json.dumps({
            "content": "I have worked with Random Forest and Decision Trees."
        }))

        # Receive follow-up question
        msg = await ws.recv()
        print("AI:", msg)

asyncio.run(test_ws())
