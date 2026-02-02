"""Client using the asyncio API."""

import asyncio
from websockets.asyncio.client import connect


async def hello(message):
    async with connect("ws://localhost:8765") as websocket:
        await websocket.send(message)
        message = await websocket.recv()
        print(message)


if __name__ == "__main__":
    while True:
        message = input("[User]: ")
        asyncio.run(hello(message))