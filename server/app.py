import asyncio
from websockets.asyncio.server import serve
import logging
import json
from server.router import handler
import server.handlers.messaging
import server.handlers.auth
import server.handlers.typing

logging.basicConfig(level=logging.INFO)

users = {}

async def websocket_handler(websocket):
    await handler(websocket, users)

async def main():
    # async with serve(handler, "0.0.0.0", 8765) as server: # listen on all interfaces
    async with serve(websocket_handler, "localhost", 8765) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())

# To allow incoming connections over TCP on port 8765
# For windows:
# Firewall -> inbound rules -> new rule -> Port 8765 TCP
# MacOS/Linux: 
# ufw allow 8765