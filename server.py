"""Echo server using the asyncio API."""

import asyncio
from websockets.asyncio.server import serve
import logging
import json

logging.basicConfig(level=logging.INFO)

users = {}
async def handle_typing(websocket, data):
    user = data.get("user")
    logging.info(f"{user} is typing...")
    # await websocket.send(json.dumps({"action": "typing", "user": user}))

async def handle_join(websocket, data):
    user = data.get("user")
    users[user] = websocket
    logging.info(f"User {user} joined")
    logging.info(users)
    # await websocket.send(json.dumps({
    #     "action": "join",
    #     "user": user,
    # }))

async def handle_message(websocket, data):
    text = data.get("text")
    sender = data.get("user")
    logging.info(f"Message received: {text}")
    for user, websocket in users.items():
        if user != sender:
            await websocket.send(json.dumps({
                "action": "message",
                "text": text,
                "user": sender,
            }))

async def handle_send_message_to_others(websocket, data):
    text = data.get("text")
    user = data.get("user")
    for user, websocket in users.items():
        if user != data.get("user"):
            await websocket.send(json.dumps({
                "action": "message",
                "text": text,
                "sender": data.get("user"),
            }))

ROUTES = {
    "join": handle_join,
    "message": handle_message,
    "typing": handle_typing,
    # "send_message_to_others": handle_send_message_to_others,
}

async def handler(websocket):
    async for raw_message in websocket:
        try:
            data = json.loads(raw_message)
            action = data.get("action")
            
            if action in ROUTES:
                await ROUTES[action](websocket, data)
            else:
                await websocket.send(json.dumps({"error": f"Unknown action: {action}"}))
        except json.JSONDecodeError:
            await websocket.send(json.dumps({"error": "Invalid JSON"}))
            
async def main():
    async with serve(handler, "localhost", 8765) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())