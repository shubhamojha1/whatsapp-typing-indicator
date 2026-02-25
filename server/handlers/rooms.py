from server.router import route
from server.models.room import Room

import logging
import json

def get_username_from_websocket(websocket, users):
    for user_id, user in users.items():  # user_id is key, user is User object
        if user.websocket == websocket:
            return user.username
    return None

def get_user_id_from_websocket(websocket, users):
    for user_id, user in users.items():  # user_id is key, user is User object
        if user.websocket == websocket:
            return user_id
    return None

@route("create_room")
async def handle_create_room(websocket, data, users, rooms):
    username = get_username_from_websocket(websocket, users)
    
    if not username:
        await websocket.send(json.dumps({
            "action": "error",
            "message": "User not authenticated"
        }))
        return
    
    room_name = data.get("room_name")
    
    # Create room with authenticated username
    new_room = Room(
        # room_id=str(uuid.uuid4()),
        room_owner=username,
        room_name=room_name,
        admins=[username],
        members=[username]
    )
    rooms[new_room.room_id] = new_room
    
    logging.info(f"Room {room_name} created by {username}")
    await websocket.send(json.dumps({
        "action": "create_room_success",
        "room_id": new_room.room_id,
        "room_name": new_room.room_name
    }))

@route("join_room")
async def handle_join_room(websocket, data, users, rooms):
    """User joins a specific room"""
    user_id = get_user_id_from_websocket(websocket, users)
    username = get_username_from_websocket(websocket, users)
    
    if not user_id or not username:
        await websocket.send(json.dumps({
            "action": "error",
            "message": "User not authenticated"
        }))
        return
    
    room_id = data.get("room_id")
    
    if room_id not in rooms:
        await websocket.send(json.dumps({
            "action": "error",
            "message": "Room not found"
        }))
        return
    
    room = rooms[room_id]
    
    # Add user to room members if not already there
    if username not in room.members:
        room.members.append(username)
    
    # Set user's current_room to this room
    users[user_id].current_room = room_id
    
    logging.info(f"User {username} joined room {room.room_name}")
    
    await websocket.send(json.dumps({
        "action": "join_room_success",
        "room_id": room_id,
        "room_name": room.room_name,
        "members": room.members
    }))
    
    # Notify other room members
    for uid, user in users.items():
        if uid != user_id and user.current_room == room_id:
            await user.websocket.send(json.dumps({
                "action": "user_joined_room",
                "username": username,
                "room_id": room_id,
                "room_name": room.room_name
            }))

@route("switch_room")
async def handle_switch_room(websocket, data, users, rooms):
    """User switches to a different room"""
    user_id = get_user_id_from_websocket(websocket, users)
    username = get_username_from_websocket(websocket, users)
    
    if not user_id or not username:
        await websocket.send(json.dumps({
            "action": "error",
            "message": "User not authenticated"
        }))
        return
    
    room_id = data.get("room_id")
    
    if room_id not in rooms:
        await websocket.send(json.dumps({
            "action": "error",
            "message": "Room not found"
        }))
        return
    
    room = rooms[room_id]
    
    # Update user's current room
    old_room_id = users[user_id].current_room
    users[user_id].current_room = room_id
    
    logging.info(f"User {username} switched to room {room.room_name}")
    
    await websocket.send(json.dumps({
        "action": "switch_room_success",
        "room_id": room_id,
        "room_name": room.room_name,
        "members": room.members
    }))

@route("list_rooms")
async def handle_list_rooms(websocket, data, users, rooms):
    """List all available rooms"""
    user_id = get_user_id_from_websocket(websocket, users)
    username = get_username_from_websocket(websocket, users)
    
    if not user_id or not username:
        await websocket.send(json.dumps({
            "action": "error",
            "message": "User not authenticated"
        }))
        return
    
    rooms_list = [
        {
            "room_id": rid,
            "room_name": room.room_name,
            "members_count": len(room.members),
            "is_member": username in room.members
        }
        for rid, room in rooms.items()
    ]
    
    await websocket.send(json.dumps({
        "action": "list_rooms",
        "rooms": rooms_list
    }))
    