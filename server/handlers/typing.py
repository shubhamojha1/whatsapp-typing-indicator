from server.router import route
import logging
import json

@route("typing")
async def handle_typing(websocket, data, users):
    user = data.get("user")
    logging.info(f"{user} is typing...")
    # Broadcast typing indicator to all OTHER users
    for other_user, ws in users.items():
        if other_user != user:
            await ws.send(json.dumps({
                "action": "typing",
                "user": user
            }))
