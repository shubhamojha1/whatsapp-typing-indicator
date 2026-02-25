from server.router import route
import logging
import json

@route("message")
async def handle_message(websocket, data, users, rooms):
    text = data.get("text")
    sender = data.get("username")
    sender_id = data.get("user_id")
    room_id = data.get("room_id")  # Get room_id from payload
    logging.info(f"Message received: {text}")
    message_type = data.get("message_type")
    
    if message_type in ["regular", "joining", "exit"]:
        # If room_id is provided, only send to room members
        if room_id:
            if room_id in rooms:
                room = rooms[room_id]
                # Only send to users who are in this room
                for user_id, user in users.items():
                    if user_id != sender_id and user.current_room == room_id:
                        await user.websocket.send(json.dumps({
                            "action": "message",
                            "text": text,
                            "username": sender,
                            "message_type": message_type,
                            "user_id": sender_id,
                            "room_id": room_id,
                            "room_name": room.room_name
                        }))
            else:
                await websocket.send(json.dumps({
                    "action": "error",
                    "message": "Room not found"
                }))
        else:
            # Default: broadcast to all users (general chat)
            for user_id, user in users.items():
                if user_id != sender_id:
                    await user.websocket.send(json.dumps({
                        "action": "message",
                        "text": text,
                        "username": sender,
                        "message_type": message_type,
                        "user_id": sender_id
                    }))
    elif message_type == "duplicate_user_error":
        await websocket.send(json.dumps({
            "action": "message",
            "text": text,
            "username": sender,
            "message_type": message_type,
            "user_id": sender_id
        }))
# TODO: IMPLEMENT SECONDARY INDEX {USERNAME: USER_ID}
@route("direct_message")
async def handle_direct_message(websocket, data, users, rooms):
    sender = data.get("username")
    receiver = data.get("receiver")
    message = data.get("message")
    # print(users.values())
    for u in users.values():
        if receiver == u.username:
            print(u.username)
    if receiver in users:
        receiver_ws = users[receiver]
        await receiver_ws.send(json.dumps({
            "action": "message",
            "username": sender,
            "receiver": receiver,
            "text": message,
            "message_type": "direct_message",
            "user_id": user_id
        }))
    else:
        await websocket.send(json.dumps({
            "action": "message",
            "username": "system",
            "text": f"User '{receiver}' not found.",
            "message_type": "regular"
        }))

@route("list_users")
async def handle_list_users(websocket, data, users, rooms):
    sender = data.get("username")
    # users_list = [key for key, _ in users.items() if key != sender]
    users_list = [u for u in users if u!=sender]
    await websocket.send(json.dumps({
        "action": "list_users",
        "users_list": users_list,
    }))
# @route("join")
# async def handle_join(websocket, data, users, rooms):
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