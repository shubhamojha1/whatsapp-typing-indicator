"""Client using the asyncio API."""

import asyncio
from websockets.asyncio.client import connect
import json

async def send_messages(websocket, user_name):
    loop = asyncio.get_event_loop()

    await websocket.send(json.dumps({
        "action": "join",
        "user": user_name
    }))

    while True:
        message = await loop.run_in_executor(None, lambda: input(f"[{user_name}]: "))

        await websocket.send(json.dumps({
            "action": "typing",
            "user": user_name
        }))

        await websocket.send(json.dumps({
            "action": "message",
            "user": user_name,
            "text": message
        }))

async def receive_messages(websocket, user_name):
    async for raw_message in websocket:
        data = json.loads(raw_message)
        action = data.get("action")
        if action == "message":
            sender = data.get("user")
            text = data.get("text")
            if sender != user_name:
                print(f"\r[{sender}]: {text}")
                print(f"[{user_name}]: ", end="", flush=True)

async def main():
    user_name = input("Enter your name: ")

    # One connection that stays open
    async with connect("ws://localhost:8765") as websocket:
        await asyncio.gather(
            send_messages(websocket, user_name),
            receive_messages(websocket, user_name)
        )

if __name__ == "__main__":
    asyncio.run(main())