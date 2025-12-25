from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.api.websockets import manager

# Initialize logging before app creation
setup_logging(log_level="DEBUG")

app = FastAPI(
    title=settings.PROJECT_NAME, 
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all origins enabled for development
# In production, this should be restricted
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Omni-Channel Dev Orchestrator API is running"}

from app.api.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Direct WebSocket Endpoint for Debugging/Reliability
@app.websocket("/ws/tasks/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: int):
    await manager.connect(websocket, task_id)
    try:
        from app.db.session import AsyncSessionLocal
        from app.models.message import Message
        import json

        while True:
            data_str = await websocket.receive_text()
            try:
                data = json.loads(data_str)
                content = data.get("content")
                sender_type = data.get("sender_type", "user")
                
                async with AsyncSessionLocal() as session:
                    msg = Message(task_id=task_id, content=content, sender_type=sender_type)
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
                print(f"WS Handling Error: {e}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, task_id)
