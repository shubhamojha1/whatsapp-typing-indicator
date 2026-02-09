"""Echo server using the asyncio API."""

import asyncio
from websockets.asyncio.server import serve
import websockets
import logging
import json

logging.basicConfig(level=logging.INFO)

users = {}
async def handle_typing(websocket, data):
    user = data.get("user")
    logging.info(f"{user} is typing...")
    # Broadcast typing indicator to all OTHER users
    for other_user, ws in users.items():
        if other_user != user:
            await ws.send(json.dumps({
                "action": "typing",
                "user": user
            }))

async def handle_join(websocket, data):
    user = data.get("user")
    if user in list(users.keys()):
        logging.info(f"User {user} already exists!")
        await websocket.send(json.dumps({
            "action": "message",
            "user": user,
            "message_type": "duplicate_user_error"
        }))
        return

    users[user] = websocket
    logging.info(f"User {user} joined")
    logging.info(users)
    await websocket.send(json.dumps({
        "action": "join",
        "user": user,
    }))

async def handle_message(websocket, data):
    text = data.get("text")
    sender = data.get("user")
    logging.info(f"Message received: {text}")
    message_type = data.get("message_type")
    if message_type == "regular" or message_type == "joining":
        for user, websocket in users.items():
                if user != sender:
                    await websocket.send(json.dumps({
                        "action": "message",
                        "text": text,
                        "user": sender,
                        "message_type": message_type
                    }))
    elif message_type == "duplicate_user_error":
        await websocket.send(json.dumps({
            "action": "message",
            "text": text,
            "user": sender,
            "message_type": message_type
        }))

async def handle_exit(websocket, data):
    user = data.get("user")
    del users[user]
    logging.info(f"{user} exited.")
    logging.info(users)
    await websocket.close(code=1000, reason = "Client Exit")

ROUTES = {
    "join": handle_join,
    "message": handle_message,
    "typing": handle_typing,
    "exit": handle_exit
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
    # async with serve(handler, "0.0.0.0", 8765) as server: # listen on all interfaces
    async with serve(handler, "localhost", 8765) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())

# To allow incoming connections over TCP on port 8765
# For windows:
# Firewall -> inbound rules -> new rule -> Port 8765 TCP
# MacOS/Linux: 
# ufw allow 8765