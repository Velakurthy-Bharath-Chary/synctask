import json
from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:
    """
    Manages all active WebSocket connections.
    Groups connections by project_id into rooms.
    """

    def __init__(self):
        # project_id -> list of connected users
        self.rooms: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, project_id: int):
        """Accept a new connection and add to project room."""
        await websocket.accept()
        if project_id not in self.rooms:
            self.rooms[project_id] = []
        self.rooms[project_id].append(websocket)

    def disconnect(self, websocket: WebSocket, project_id: int):
        """Remove a connection from the project room."""
        if project_id in self.rooms:
            try:
                self.rooms[project_id].remove(websocket)
            except ValueError:
                pass
            # Clean up empty rooms
            if not self.rooms[project_id]:
                del self.rooms[project_id]

    async def broadcast_to_project(self, project_id: int, message: dict):
        """Send a message to ALL users connected to a project."""
        if project_id not in self.rooms:
            return

        disconnected = []
        payload = json.dumps(message)

        for connection in self.rooms[project_id]:
            try:
                await connection.send_text(payload)
            except Exception:
                # Connection is broken, mark for removal
                disconnected.append(connection)

        # Clean up broken connections
        for conn in disconnected:
            self.disconnect(conn, project_id)

# One shared instance used across the entire app
ws_manager = ConnectionManager()
"""What this file does:

Keeps track of all connected users per project
When a task is updated, broadcast_to_project sends the update to everyone in that project instantly
Automatically removes users who disconnect"""