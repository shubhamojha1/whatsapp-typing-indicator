"""Client using the asyncio API."""

import asyncio
from websockets.asyncio.client import connect
import json
import sys
import subprocess
import time
import os

# Cursor region agent log
# LOG_PATH = r"c:\Users\subha\Projects\blog_projects\whatsapp-typing-indicator\.cursor\debug.log"
# def log_debug(session_id, run_id, hypothesis_id, location, message, data):
#     try:
#         with open(LOG_PATH, "a", encoding="utf-8") as f:
#             f.write(json.dumps({"sessionId": session_id, "runId": run_id, "hypothesisId": hypothesis_id, "location": location, "message": message, "data": data, "timestamp": time.time() * 1000}) + "\n")
#     except: pass
# # #endregion

async def send_messages(websocket, user_name, state):
    await websocket.send(json.dumps({
        "action": "join",
        "user": user_name
    }))

    detector_path = "./keystroke_detector.exe" if sys.platform == "win32" else "./keystroke_detector"
    
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
        while True:
            try:
                line = await proc.stdout.readline()
            except Exception as e:
                print(f"Error reading from subprocess: {e}")
                break
            
            if not line:
                break
            
            line = line.decode().rstrip('\n')

            # if line.startswith("SPACE"):
            #     if current_message:
            #         current_message.append("-")
            #         state["buffer"] = "".join(current_message)
            #         state["typing"] = True
            #         print(" ", end="", flush=True)
            
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
                    await websocket.send(json.dumps({
                        "action": "typing",
                        "user": user_name
                    }))
                    last_typing_time = current_time
                
            elif line == "ENTER":
                # Enter pressed - send the complete message
                print()  # New line after Enter
                message_text = "".join(current_message)
                print("current_message --> ", current_message)
                print("message_text -->", message_text.split())
                if message_text == "/exit":
                    await websocket.send(json.dumps({
                        "action": "exit",
                        "user": user_name,
                        "text": message_text
                    }))
                    break
                elif message_text == "/users":
                    await websocket.send(json.dumps({
                        "action": "list_users",
                        "user": user_name
                    }))
                elif message_text.startswith("/dm "):
                    parts = message_text.split()
                    if len(parts) >= 3:
                        receiver = parts[1].lstrip("@")
                        message = " ".join(parts[2:])
                        print(f"dm to {receiver}: {message}")
                        await websocket.send(json.dumps({
                            "action": "direct_message",
                            "user": user_name,
                            "receiver": receiver,
                            "message": message
                        }))
                    else:
                        print("Usage: /dm @username message")
                elif message_text:  # Only send non-empty messages
                    await websocket.send(json.dumps({
                        "action": "message",
                        "user": user_name,
                        "text": message_text,
                        "message_type": "regular"
                    }))
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
                # Ctrl+C or EOF detected - exit
                
                break
    finally:
        if proc.returncode is None:
            proc.terminate()
            try:
                await proc.wait()
            except Exception:
                pass

async def receive_messages(websocket, user_name, state):
    async for raw_message in websocket:
        data = json.loads(raw_message)
        action = data.get("action")
        
        if action == "typing":
            sender = data.get("user")
            if sender != user_name:
                # Display typing indicator (clear line, show typing, restore prompt)
                print(f"\r\033[K{sender} is typing...", end="", flush=True)
                await asyncio.sleep(1)  # Show for 1 second
                current_text = state.get("buffer", "")
                print(f"\r\033[K[{user_name}]: {current_text}", end="", flush=True)
                
        elif action == "message":
            sender = data.get("user")
            text = data.get("text")
            message_type = data.get("message_type")
            # print("MESSAGE TYPE -> ", message_type)
            # try:
            print("INSIDE MESSAGE")
            if message_type == "duplicate_user_error":
                print(f"User {sender} already exists!")
                await websocket.send(json.dumps({
                    "action": "exit",
                    "user": sender,
                    "text": text
                }))
                raise SystemExit(1)
            # except SystemExit:
            #     print("Please launch client again!")s
            elif message_type == "direct_message" and data.get("receiver") == user_name:
                print(f"\r\033[K[DM] [{sender}]: {text}")

            if sender != user_name:
                print(f"\r\033[K[{sender}]: {text}")
                current_text = state.get("buffer", "")
                print(f"[{user_name}]: {current_text}", end="", flush=True)
        
        elif action == "join":
            sender = data.get("user")
            # print()
            # message_type = data.get("message_type")
            # if message_type == "duplicate_user_error":
            #     message_text = f"\r\033[K[ User {sender} already exists! ]"
            #     await websocket.send(json.dumps({
            #         "action": "message",
            #         "user": sender,
            #         "text": message_text,
            #         "message_type": "duplicate_user_error"
            #     }))

            message_text = f"\r\033[K[ User {sender} joined! ]"
            await websocket.send(json.dumps({
                        "action": "message",
                        "user": user_name,
                        "text": message_text,
                        "message_type": "joining"
                    }))
            
        elif action == "exit":
            sender = data.get("user")
            message_text = f"\r\033[K[ User {sender} left! ]"
            await websocket.send(json.dumps({
                        "action": "message",
                        "user": user_name,
                        "text": message_text,
                        "message_type": "exit"
            }))
        
        elif action == "list_users":
            users_list = data.get("users_list")
            print(users_list)

        elif action == "direct_message":
            sender = data.get("user")
            receiver = data.get("receiver")
            message = data.get("message")
            if receiver == user_name:
                print(f"\r\033[K[{sender}]: [DM] {message}")


async def main():
    user_name = input("Enter your name: ")
    state = {"buffer": "", "typing": False} # Global state to track the current message and typing status

    # One connection that stays open
    # server_host = input("Server address (or press Enter for localhost): ").strip() or "localhost"
    # async with connect(f"ws://{server_host}:8765") as websocket:
    async with connect("ws://localhost:8765") as websocket:
        await asyncio.gather(
            send_messages(websocket, user_name, state),
            receive_messages(websocket, user_name, state)
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except SystemExit:
        pass