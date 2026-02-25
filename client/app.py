"""Client using the asyncio API."""

import asyncio
from websockets.asyncio.client import connect
import json
import sys
# import subprocess
import time
import pathlib
# import os

from protocol.payloads import ClientJoinPayload

async def handle_client_exit(websocket, user_name):
    await websocket.send(json.dumps({
        "action": "exit",
        "username": user_name,
        # "text": message_text
    }))

async def handle_client_list_users(websocket, user_name):
    await websocket.send(json.dumps({
                        "action": "list_users",
                        "username": user_name
                    }))
    return
    
async def handle_client_direct_message(websocket, user_name, message_text):
    parts = message_text.split()
    if len(parts) >= 3:
        receiver = parts[1].lstrip("@")
        message = " ".join(parts[2:])
        print(f"dm to {receiver}: {message}")
        await websocket.send(json.dumps({
            "action": "direct_message",
            "username": user_name,
            "receiver": receiver,
            "message": message,
            # "user_id": user.user_id
        }))
    else:
        print("Usage: /dm @username message")

async def handle_client_create_room(websocket, user_name, message_text, is_admin, state):
    if not is_admin:
        print("Only admins can create rooms!")
        return
    # print("CREATING ROOOOOOOOOOOOOOOOOOM!")
    # /create-room #general
    # if len(parts)
    parts = message_text.split()
    if len(parts) >=3:
        print("Room name cant have spaces!")
        return
    if len(parts) < 2:
        print("Invalid syntax!")
        return
    room_name = parts[1].lstrip("#")
    print("roooomm => ", room_name)
    print("RRRRROOOOMMMM => ", parts)
    await websocket.send(json.dumps({
        "action": "create_room",
        # "room_owner": user_name,
        "room_name": room_name
    }))

async def handle_client_join_room(websocket, user_name, message_text, state):
    """User joins a specific room"""
    parts = message_text.split()
    if len(parts) < 2:
        print("Usage: /join-room <room_id>")
        return
    room_id = parts[1]
    await websocket.send(json.dumps({
        "action": "join_room",
        "room_id": room_id
    }))

async def handle_client_switch_room(websocket, user_name, message_text, state):
    """User switches to a different room"""
    parts = message_text.split()
    if len(parts) < 2:
        print("Usage: /switch-room <room_id>")
        return
    room_id = parts[1]
    await websocket.send(json.dumps({
        "action": "switch_room",
        "room_id": room_id
    }))

async def handle_client_list_rooms(websocket, user_name, state):
    """List all available rooms"""
    await websocket.send(json.dumps({
        "action": "list_rooms"
    }))
    



async def send_messages(websocket, user_name, state, stop_event, admin_flag):
    client_join_payload = ClientJoinPayload(action="join", username=user_name, admin_flag=admin_flag)
    await websocket.send(client_join_payload.model_dump_json())

    project_root = pathlib.Path(__file__).parent.parent
    detector_name = "keystroke_detector.exe" if sys.platform == "win32" else "keystroke_detector"
    detector_path = str(project_root / detector_name)
    
    # Create keystroke detector subprocess once at the start
    proc = await asyncio.create_subprocess_exec(
        detector_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    # Initialize message buffer and typing debounce
    current_message = []
    last_typing_time = 0
    TYPING_DEBOUNCE_SECONDS = 2.0
    print(f"[{user_name}]: ", end="", flush=True)
    
    # Give subprocess a moment to initialize
    await asyncio.sleep(0.1)
    # Read keystrokes continuously from the subprocess
    try:
        while not stop_event.is_set():
            try:
                line = await asyncio.wait_for(proc.stdout.readline(), timeout=0.5)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Error reading from subprocess: {e}")
                break
            
            if not line:
                break
            
            line = line.decode().rstrip('\n')
            
            if line.startswith("KEY:"):
                # Regular key pressed - add to message buffer
                char = line[4:]  # Get character after "KEY:"
                if char == "":
                    continue
                current_message.append(char)
                state["buffer"] = "".join(current_message)
                state["typing"] = True
                # Echo the character to screen
                print(char, end="", flush=True) 
                
                # Send typing indicator asynchronously (with debouncing)
                current_time = time.time()
                if current_time - last_typing_time > TYPING_DEBOUNCE_SECONDS:
                    typing_payload = {
                        "action": "typing",
                        "username": user_name,
                    }
                    # Add room_id if user is in a room
                    if state.get("current_room_id"):
                        typing_payload["room_id"] = state["current_room_id"]
                    await websocket.send(json.dumps(typing_payload))
                    last_typing_time = current_time
                
            elif line == "ENTER":
                # Enter pressed - send the complete message
                print()  # New line after Enter
                message_text = "".join(current_message)
                # print("current_message --> ", current_message)
                # print("message_text -->", message_text.split())
                current_text = state.get("buffer", "")

                if current_message and current_message[0] == "/":
                    # print("special command -> ", message_text.split()[0])
                    command = message_text.split()[0]

                    if command == "/exit":
                        await handle_client_exit(websocket=websocket, user_name=user_name)
                        break
                    elif command == "/users":
                        await handle_client_list_users(websocket=websocket, user_name=user_name)
                        # print(f"\r\033[K[{user_name}]: {current_text}", end="", flush=True)
                    elif command == "/dm":
                        await handle_client_direct_message(websocket=websocket, user_name=user_name, message_text=message_text)
                    elif command == "/create-room":
                        await handle_client_create_room(websocket=websocket, user_name=user_name, message_text=message_text, is_admin=admin_flag, state=state)
                    elif command == "/join-room":
                        await handle_client_join_room(websocket=websocket, user_name=user_name, message_text=message_text, state=state)
                    elif command == "/switch-room":
                        await handle_client_switch_room(websocket=websocket, user_name=user_name, message_text=message_text, state=state)
                    elif command == "/list-rooms":
                        await handle_client_list_rooms(websocket=websocket, user_name=user_name, state=state)
                elif message_text:  # Only send non-empty messages
                    msg_payload = {
                        "action": "message",
                        "username": user_name,
                        "text": message_text,
                        "message_type": "regular"
                    }
                    # Add room_id if user is in a room
                    if state.get("current_room_id"):
                        msg_payload["room_id"] = state["current_room_id"]
                    await websocket.send(json.dumps(msg_payload))
                current_message = []  # Reset for next message
                state["buffer"] = ""
                state["typing"] = False
                print(f"[{user_name}]: ", end="", flush=True)
                
            elif line == "BACKSPACE":
                # Backspace pressed - remove last character
                if current_message:
                    current_message.pop()
                    state["buffer"] = "".join(current_message)
                    state["typing"] = True
                    # Erase character on screen: backspace, space, backspace
                    print("\b \b", end="", flush=True)
                    
            elif line == "EXIT":
                break
    finally:
        if proc.returncode is None:
            proc.terminate()
            try:
                await proc.wait()
            except Exception:
                pass

async def receive_messages(websocket, user_name, state, stop_event, admin_flag):
    async for raw_message in websocket:
        data = json.loads(raw_message)
        action = data.get("action")
        
        if action == "typing":
            sender = data.get("username")
            if sender != user_name:
                # Display typing indicator (clear line, show typing, restore prompt)
                print(f"\r\033[K{sender} is typing...", end="", flush=True)
                await asyncio.sleep(1)  # Show for 1 second
                current_text = state.get("buffer", "")
                room_header = f"[{state.get('current_room_name', 'GENERAL CHAT')}]" if state.get("current_room_id") else "[GENERAL CHAT]"
                print(f"\r\033[K{room_header}\n[{user_name}]: {current_text}", end="", flush=True)
                
        elif action == "message":
            sender = data.get("username")
            text = data.get("text")
            message_type = data.get("message_type")
            room_name = data.get("room_name", "GENERAL CHAT")
            
            if message_type == "duplicate_user_error":
                print(f"username {sender} already exists!")
                stop_event.set()
                return
            elif message_type == "direct_message" and data.get("receiver") == user_name:
                print(f"\r\033[K[DM] [{sender}]: {text}")
                current_text = state.get("buffer", "")
                room_header = f"[{state.get('current_room_name', 'GENERAL CHAT')}]" if state.get("current_room_id") else "[GENERAL CHAT]"
                print(f"{room_header}\n[{user_name}]: {current_text}", end="", flush=True)

            elif sender != user_name:
                room_header = f"[{room_name}]" if room_name != "GENERAL CHAT" else "[GENERAL CHAT]"
                print(f"\r\033[K{room_header}\n[{sender}]: {text}")
                current_text = state.get("buffer", "")
                print(f"[{user_name}]: {current_text}", end="", flush=True)
        
        elif action == "join":
            username = data.get("username")
            user_id = data.get("user_id")
            message_text = f"\r\033[K[ username {username} joined! ]"
            print("\r\033[K\t\t[GENERAL CHAT]\r\n\n")
            await websocket.send(json.dumps({
                        "action": "message",
                        "username": user_name,
                        "text": message_text,
                        "message_type": "joining",
                        "user_id": user_id
                    }))
            
        elif action == "exit":
            sender = data.get("username")
            message_text = f"\r\033[K[ username {sender} left! ]"
            await websocket.send(json.dumps({
                        "action": "message",
                        "username": user_name,
                        "text": message_text,
                        "message_type": "exit"
            }))
        
        elif action == "list_users":
            users_list = data.get("users_list")
            print(users_list)

        elif action == "create_room_success":
            # print("SUCCCESSSS")
            room_name = data.get("room_name")
            room_id = data.get("room_id")
            state["current_room_id"] = room_id
            state["current_room_name"] = room_name
            print(f"\r\033[K\t\t[{room_name}]\r\n\n")

        elif action == "join_room_success":
            room_name = data.get("room_name")
            room_id = data.get("room_id")
            members = data.get("members", [])
            state["current_room_id"] = room_id
            state["current_room_name"] = room_name
            print(f"\r\033[K\t\t[{room_name}]\r\nMembers: {', '.join(members)}\r\n\n")

        elif action == "switch_room_success":
            room_name = data.get("room_name")
            room_id = data.get("room_id")
            members = data.get("members", [])
            state["current_room_id"] = room_id
            state["current_room_name"] = room_name
            print(f"\r\033[K\t\t[{room_name}]\r\nMembers: {', '.join(members)}\r\n\n")

        elif action == "user_joined_room":
            joined_user = data.get("username")
            room_name = data.get("room_name")
            print(f"\r\033[K[ {joined_user} joined {room_name}! ]")
            current_text = state.get("buffer", "")
            print(f"[{user_name}]: {current_text}", end="", flush=True)

        elif action == "list_rooms":
            rooms = data.get("rooms", [])
            print("\r\033[K\n=== Available Rooms ===")
            for room in rooms:
                member_status = "✓ Member" if room["is_member"] else "○ Not Member"
                print(f"- {room['room_name']} (ID: {room['room_id']}) - {room['members_count']} members [{member_status}]")
            print("========================\n")
            current_text = state.get("buffer", "")
            print(f"[{user_name}]: {current_text}", end="", flush=True)

        elif action == "error":
            message = data.get("message")
            print(f"\r\033[K[ERROR]: {message}")
            current_text = state.get("buffer", "")
            room_header = f"[{state.get('current_room_name', 'GENERAL CHAT')}]" if state.get("current_room_id") else "[GENERAL CHAT]"
            print(f"{room_header}\n[{user_name}]: {current_text}", end="", flush=True)

async def main():
    admin_flag = len(sys.argv) > 1 and sys.argv[1] == "--admin"
    if admin_flag:
        admin_username = input("Enter admin username: ")
        admin_password = input("Enter admin password: ")
        if admin_username == "admin" and admin_password == "admin":
            print("Admin mode enabled")
        else:
            print("Invalid admin credentials")
            sys.exit(1) 
    user_name = admin_username if admin_flag else input("Enter your name: ")
    state = {
        "buffer": "", 
        "typing": False,
        "current_room_id": None,  # Track current room
        "current_room_name": None
    }  # Global state to track the current message and typing status

    # One connection that stays open
    # server_host = input("Server address (or press Enter for localhost): ").strip() or "localhost"
    # async with connect(f"ws://{server_host}:8765") as websocket:
    async with connect("ws://localhost:8765") as websocket:
        stop_event = asyncio.Event()
        await asyncio.gather(
            send_messages(websocket, user_name, state, stop_event, admin_flag),
            receive_messages(websocket, user_name, state, stop_event, admin_flag)
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except SystemExit:
        pass