"""Echo server using the asyncio API."""

import asyncio
from websockets.asyncio.server import serve
import logging

logging.basicConfig(level=logging.INFO)

async def echo(websocket):
    async for message in websocket:
        logging.info(f"Received: {message}")
        await websocket.send("Echo:" +message)


async def main():
    async with serve(echo, "localhost", 8765) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())