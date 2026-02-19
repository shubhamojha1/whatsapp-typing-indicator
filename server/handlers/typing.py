from server.router import route
import logging
import json

@route("typing")
async def handle_typing(websocket, data, users):
    username = data.get("username")
    logging.info(f"{username} is typing...")
    # Broadcast typing indicator to all OTHER users
    for user_id, user in users.items():
        if user.username != username:
            await user.websocket.send(json.dumps({
                "action": "typing",
                "username": username
            }))
