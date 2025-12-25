from typing import Any, Dict
from fastapi import APIRouter, Header, HTTPException, Body
from app.core.event_bus import event_bus
from app.schemas.events import EventTaskUpdate, EventMessage, EventType
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
    
    # 1. Transform Payload to Event
    # In a real app, we would process 'source' specific logic here.
    # For now, we assume it's a generic update or message.
    
    event_type = payload.get("type", "system_alert")
    
    if event_type == "message":
        # Simulate incoming chat message
        event = EventMessage(
            data={
                "content": payload.get("content", "New message"),
                "sender": source,
                "sender_type": "user" # or 'system'
            },
            task_id=payload.get("task_id")
        )
    elif event_type == "task_update":
         event = EventTaskUpdate(
            data={
                "status": payload.get("status"),
                "description": f"Updated by {source}"
            },
            task_id=payload.get("task_id")
        )
    else:
        # Generic Alert
         # We need to construct a base event or extend schema
         # For now using generic message type for alerts to visualize
         event = EventMessage(
             type=EventType.SYSTEM_ALERT,
             data={"message": f"Alert from {source}: {payload}"}
         )
    
    # 2. Publish to Bus
    await event_bus.publish(event)
    
    return {"status": "accepted", "event_id": str(event.timestamp)}
