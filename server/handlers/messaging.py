from server.router import route
import logging
import json

@route("message")
async def handle_message(websocket, data, users):
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

@route("direct_message")
async def handle_direct_message(websocket, data, users):
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

@route("list_users")
async def handle_list_users(websocket, data, users):
    sender = data.get("user")
    # users_list = [key for key, _ in users.items() if key != sender]
    users_list = [u for u in users if u!=sender]
    await websocket.send(json.dumps({
        "action": "list_users",
        "users_list": users_list,
    }))
# @route("join")
# async def handle_join(websocket, data, users):
#     user = data.get("user")
#     if user in users:
#         logging.info(f"User {user} already exists!")
#         await websocket.send(json.dumps({
#             "action": "message",
#             "user": user,
#             "message_type": "duplicate_user_error"
#         }))
#         return

#     users[user] = websocket
#     logging.info(f"User {user} joined")
#     await websocket.send(json.dumps({
#         "action": "join",
#         "user": user,
#     }))