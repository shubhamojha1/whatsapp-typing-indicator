import json

ROUTES = {}

def route(action_name):
    def decorator(func):
        ROUTES[action_name] = func
        return func
    return decorator

async def handler(websocket, users):
    async for raw_message in websocket:
        try:
            data = json.loads(raw_message)
            action = data.get("action")
            
            if action in ROUTES:
                await ROUTES[action](websocket, data, users)
            else:
                await websocket.send(json.dumps({"error": f"Unknown action: {action}"}))
        except json.JSONDecodeError:
            await websocket.send(json.dumps({"error": "Invalid JSON"}))