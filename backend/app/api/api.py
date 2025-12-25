from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.api.endpoints import tasks, webhooks, auth, messages, stream, brain_test, agent_runner
from app.api.websockets import manager
from app.api import deps

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(brain_test.router, prefix="/brain", tags=["brain"])
api_router.include_router(agent_runner.router, prefix="/agent", tags=["agent"])
# The endpoint is defined as @router.get("/stream"), so including it without prefix makes it /api/v1/stream
api_router.include_router(stream.router, tags=["stream"])

@api_router.websocket("/ws/tasks/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: int):
    # This remains for backward compat or input streaming if needed
    await manager.connect(websocket, task_id)
    try:
        from app.db.session import AsyncSessionLocal
        from app.models.message import Message, SenderType
        import json

        while True:
            data_str = await websocket.receive_text()
            try:
                data = json.loads(data_str)
                content = data.get("content")
                sender_type = data.get("sender_type", "user") 
                
                async with AsyncSessionLocal() as session:
                    msg = Message(
                        task_id=task_id,
                        content=content,
                        sender_type=sender_type
                    )
                    session.add(msg)
                    await session.commit()
                    await session.refresh(msg)
                    
                    msg_dict = {
                        "id": msg.id,
                        "task_id": msg.task_id,
                        "content": msg.content,
                        "sender_type": msg.sender_type,
                        "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
                    }
                    await manager.broadcast_to_task(task_id, msg_dict)
                    
            except Exception as e:
                print(f"Error processing WS message: {e}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, task_id)
