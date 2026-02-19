from server.router import route
from server.models.user import User, UserRole

from protocol.payloads import ServerJoinPayload

import logging
import json

def register_user(users, username, is_admin=False):
    if any(user.username == username for user in users.values()):
        return None, "duplicate"

    user = User(username, websocket=None)
    if is_admin:
        user.user_role = UserRole.ADMIN

    users[user.user_id] = user
    return user, None

@route("join")
async def handle_join(websocket, data, users):
    username = data.get("username")
    is_admin = data.get("admin_flag")
    user, error = register_user(users, username, is_admin)
    if error:
    # if username in users:
        logging.info(f"User {username} already exists!")
        await websocket.send(json.dumps({
            "action": "message",
            "username": username,
            "message_type": "duplicate_user_error",
            "user_id": user.user_id
        })) 
        return
    
    user.websocket = websocket
    logging.info(f"User {username} joined")
    server_join_payload = ServerJoinPayload(action="join", username=username, user_id=user.user_id)
    await websocket.send(server_join_payload.model_dump_json())

@route("exit")
async def handle_exit(websocket, data, users):
    username = data.get("username")
    users.pop(username, None)
    logging.info(f"{username} exited.")
    await websocket.send(json.dumps({
        "action": "exit",
        "username": username,
    }))
    await websocket.close(code=1000, reason="Client Exit")
