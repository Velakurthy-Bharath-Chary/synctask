from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import JWTError
from app.core.security import decode_token
from app.core.ws_manager import ws_manager

router = APIRouter(tags=["WebSocket"])

@router.websocket("/ws/{project_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    project_id: int,
    token: str = Query(...)
):
    # Verify JWT token before accepting connection
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
        if not user_id:
            await websocket.close(code=4001)
            return
    except JWTError:
        await websocket.close(code=4001)
        return

    # Connect user to project room
    await ws_manager.connect(websocket, project_id)

    try:
        # Tell user they are connected
        await websocket.send_json({
            "event": "connected",
            "project_id": project_id,
            "message": "Real-time sync active"
        })

        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, project_id)
"""

**What these two files do:**

`analytics.py`:
```
GET /analytics/projects/{id}
→ Checks membership
→ Returns charts data
```

`websocket.py`:
```
ws://localhost:8000/ws/{project_id}?token=...
→ Verifies JWT token
→ Adds user to project room
→ Keeps connection alive
→ Listens for ping → replies pong"""