import asyncio
from websockets.asyncio.server import serve
import logging
import json
from server.router import handler

# Registering routes
import server.handlers.messaging
import server.handlers.auth
import server.handlers.typing

logging.basicConfig(level=logging.INFO)

# Better for testing
# New state for each test, and cleaner
def create_users_store():
    return {}

async def websocket_handler(websocket, users):
    await handler(websocket, users)

async def create_server(host="localhost", port=8765):
    users = create_users_store()
    return await serve(lambda ws: websocket_handler(ws, users), host, port)

async def main():
    # async with serve(handler, "0.0.0.0", 8765) as server: # listen on all interfaces
    # async with serve(websocket_handler, "localhost", 8765) as server:
    #     await server.serve_forever()
    async with await create_server() as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())

# To allow incoming connections over TCP on port 8765
# For windows:
# Firewall -> inbound rules -> new rule -> Port 8765 TCP
# MacOS/Linux: 
# ufw allow 8765