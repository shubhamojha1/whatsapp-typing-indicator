from server.router import route
import logging
import json

@route("typing")
async def handle_typing(websocket, data, users, rooms):
    username = data.get("username")
    room_id = data.get("room_id")  # Get room_id from payload
    logging.info(f"{username} is typing...")
    
    # If room_id is provided, only broadcast to room members
    if room_id:
        if room_id in rooms:
            # Only send to users in the same room
            for user_id, user in users.items():
                if user.username != username and user.current_room == room_id:
                    await user.websocket.send(json.dumps({
                        "action": "typing",
                        "username": username,
                        "room_id": room_id
                    }))
    else:
        # Default: broadcast to all OTHER users (general chat)
        for user_id, user in users.items():
            if user.username != username:
                await user.websocket.send(json.dumps({
                    "action": "typing",
                    "username": username
                }))
