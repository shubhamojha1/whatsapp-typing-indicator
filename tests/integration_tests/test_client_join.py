import pytest
import json
import websockets
from server.app import create_server

@pytest.mark.asyncio
async def test_client_join_success():
    server = await create_server(port=0)
    port = server.sockets[0].getsockname()[1]
    assert port > 0

    async with server:
        async with websockets.connect(f"ws://localhost:{port}") as websocket:
            assert websocket is not None
            join_payload = {
                "action": "join",
                "username": "alice",
                "admin_flag": False
            }

            await websocket.send(json.dumps(join_payload))
            
            response = await websocket.recv()
            response_json = json.loads(response)  
            assert response_json["action"] == "join"
            assert response_json["username"] == "alice"
            assert "user_id" in response_json