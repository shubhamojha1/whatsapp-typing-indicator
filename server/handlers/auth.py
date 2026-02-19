from server.router import route
from server.models.user import User, UserRole
import logging
import json

@route("join")
async def handle_join(websocket, data, users):
    username = data.get("username")
    if username in users:
        logging.info(f"User {username} already exists!")
        await websocket.send(json.dumps({
            "action": "message",
            "username": username,
            "message_type": "duplicate_user_error"
        }))
        return

    is_admin = data.get("admin_flag")
    user = User(username = username, websocket = websocket)
    if is_admin:
        user.user_role = UserRole.ADMIN
    users[user.user_id] = user
    # username_index[username] = user.user_id
    # print("----")
    # for user_id, user in users.items():
    #     print(user.username)
    #     print(user.user_id)
    #     print(user.websocket)
    #     print(user.user_role.value)
    # print("----")
    logging.info(f"User {username} joined")
    await websocket.send(json.dumps({
        "action": "join",
        "username": username,
        "user_id": user.user_id
    }))

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
