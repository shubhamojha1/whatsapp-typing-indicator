"""Client using the asyncio API."""

import asyncio
from websockets.asyncio.client import connect
import json

async def send_action(action, **data):
    async with connect("ws://localhost:8765") as websocket:
        payload = {
            "action": action,
            **data
        }
        await websocket.send(json.dumps(payload))
        response = await websocket.recv()
        print(json.loads(response))

if __name__ == "__main__":
    user_name = input("Enter your name: ")
    asyncio.run(send_action("join", user=user_name))
    while True:
        message = input(f"[{user_name}]: ")
        asyncio.run(send_action("typing", user=user_name))
        asyncio.run(send_action("message", user=user_name, text=message))