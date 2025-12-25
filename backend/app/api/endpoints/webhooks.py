from typing import Any, Dict
from fastapi import APIRouter, Header, HTTPException, Body
from app.core.event_bus import event_bus
from app.schemas.events import EventTaskUpdate, EventMessage, EventLog, EventArtifact, EventType, EventBase
from pydantic import BaseModel

router = APIRouter()

class WebhookPayload(BaseModel):
    source: str
    data: Dict[str, Any]

@router.post("/ingest/{source}")
async def ingest_webhook(source: str, payload: Dict[str, Any] = Body(...)):
    """
    Simulates receiving a webhook from an external source (WhatsApp, Email, etc.)
    and pushing an event to the internal Event Bus.
    """
    print(f"Received webhook from {source}: {payload}")
    
    event_type = payload.get("type", "system_alert")
    task_id = payload.get("task_id")
    
    event: EventBase = None

    if source == "simulation":
        # Direct Pass-through for E2E Testing
        if event_type == "terminal_log":
            event = EventLog(task_id=task_id, data=payload.get("data"))
        elif event_type == "artifact_update":
            event = EventArtifact(task_id=task_id, data=payload.get("data"))
        elif event_type == "new_message":
            event = EventMessage(task_id=task_id, data=payload.get("data"))
            
    if not event:
        # Standard Logic
        if event_type == "message":
            event = EventMessage(
                data={
                    "content": payload.get("content", "New message"),
                    "sender": source,
                    "sender_type": "user"
                },
                task_id=task_id
            )
        elif event_type == "task_update":
             event = EventTaskUpdate(
                data={
                    "status": payload.get("status"),
                    "description": f"Updated by {source}"
                },
                task_id=task_id
            )
        else:
             event = EventMessage(
                 type=EventType.SYSTEM_ALERT,
                 data={"message": f"Alert from {source}: {payload}"}
             )
    
    if event:
        await event_bus.publish(event)
        return {"status": "accepted", "event_id": str(event.timestamp)}
    
    return {"status": "ignored"}
