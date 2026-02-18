from server.router import route
import logging
import json

@route("join")
async def handle_join(websocket, data, users):
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
    await websocket.send(json.dumps({
        "action": "join",
        "user": user,
    }))