from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.api.endpoints import tasks, webhooks
from app.api.websockets import manager
from app.api import deps

api_router = APIRouter()
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])

@api_router.websocket("/ws/tasks/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: int):
    await manager.connect(websocket, task_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo logic or handle incoming messages from frontend defaults
            # For now we use WS mainly for server->client pushes
            await manager.broadcast_to_task(task_id, {"type": "ping", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket, task_id)
