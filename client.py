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
            
            line = line.decode().strip()
            
            if line.startswith("KEY:"):
                # Regular key pressed - add to message buffer
                char = line[4:]  # Get character after "KEY:"
                current_message.append(char)
                state["buffer"] = "".join(current_message)
                state["typing"] = True
                # Echo the character to screen
                if char == " ":
                    print(" ", end="", flush=True)
                else:
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
                if message_text:  # Only send non-empty messages
                    await websocket.send(json.dumps({
                        "action": "message",
                        "user": user_name,
                        "text": message_text
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
            if sender != user_name:
                print(f"\r\033[K[{sender}]: {text}")
                current_text = state.get("buffer", "")
                print(f"[{user_name}]: {current_text}", end="", flush=True)

async def main():
    user_name = input("Enter your name: ")
    state = {"buffer": "", "typing": False} # Global state to track the current message and typing status

    # One connection that stays open
    async with connect("ws://localhost:8765") as websocket:
        await asyncio.gather(
            send_messages(websocket, user_name, state),
            receive_messages(websocket, user_name, state)
        )

if __name__ == "__main__":
    asyncio.run(main())