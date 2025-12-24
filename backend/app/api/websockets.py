from typing import List, Dict
from fastapi import WebSocket
from app.core.logging_config import log

class ConnectionManager:
    def __init__(self):
        # Map task_id to list of active websockets
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, task_id: int):
        await websocket.accept()
        if task_id not in self.active_connections:
            self.active_connections[task_id] = []
        self.active_connections[task_id].append(websocket)
        log.info(f"WebSocket connected for task {task_id}")

    def disconnect(self, websocket: WebSocket, task_id: int):
        if task_id in self.active_connections:
            if websocket in self.active_connections[task_id]:
                self.active_connections[task_id].remove(websocket)
                if not self.active_connections[task_id]:
                    del self.active_connections[task_id]
        log.info(f"WebSocket disconnected for task {task_id}")

    async def broadcast_to_task(self, task_id: int, message: dict):
        if task_id in self.active_connections:
            for connection in self.active_connections[task_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    log.error(f"Error broadcasting to task {task_id}: {e}")

manager = ConnectionManager()
