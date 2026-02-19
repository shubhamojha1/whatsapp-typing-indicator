import pytest 
import websockets

from server.app import create_server

@pytest.mark.asyncio
async def test_server_startup():
    server = await create_server(port=0) # OS picks free port
    port = server.sockets[0].getsockname()[1]
    assert port > 0
    # await server.close()

    async with server:
        async with websockets.connect(f"ws://localhost:{port}") as websocket:
            # Connection should be successful
            assert websocket is not None
    