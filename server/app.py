import asyncio
from websockets.asyncio.server import serve
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
    if user in users:
        logging.info(f"User {user} already exists!")
        await websocket.send(json.dumps({
            "action": "message",
            "user": user,
            "message_type": "duplicate_user_error"
        }))
        return

    users[user] = websocket
    logging.info(f"User {user} joined")
    # logging.info(users)
    await websocket.send(json.dumps({
        "action": "join",
        "user": user,
    }))

async def handle_message(websocket, data):
    text = data.get("text")
    sender = data.get("user")
    logging.info(f"Message received: {text}")
    message_type = data.get("message_type")
    if message_type in ["regular", "joining", "exit"]:
        for user, ws in users.items():
                if user != sender:
                    await ws.send(json.dumps({
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
    # del users[user]
    users.pop(user, None)
    logging.info(f"{user} exited.")
    # logging.info(users)
    await websocket.send(json.dumps({
        "action": "exit",
        "user": user,
    }))
    await websocket.close(code=1000, reason="Client Exit")

async def handle_list_users(websocket, data):
    sender = data.get("user")
    # users_list = [key for key, _ in users.items() if key != sender]
    users_list = [u for u in users if u!=sender]
    await websocket.send(json.dumps({
        "action": "list_users",
        "users_list": users_list,
    }))

async def handle_direct_message(websocket, data):
    sender = data.get("user")
    receiver = data.get("receiver")
    message = data.get("message")

    if receiver in users:
        receiver_ws = users[receiver]
        await receiver_ws.send(json.dumps({
            "action": "message",
            "user": sender,
            "receiver": receiver,
            "text": message,
            "message_type": "direct_message"
        }))
    else:
        await websocket.send(json.dumps({
            "action": "message",
            "user": "system",
            "text": f"User '{receiver}' not found.",
            "message_type": "regular"
        }))


ROUTES = {
    "join": handle_join,
    "message": handle_message,
    "typing": handle_typing,
    "exit": handle_exit,
    "list_users": handle_list_users,
    "direct_message": handle_direct_message
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