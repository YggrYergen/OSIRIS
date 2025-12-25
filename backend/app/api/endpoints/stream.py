import asyncio
import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from app.core.event_bus import event_bus
from app.schemas.events import EventBase, EventType

router = APIRouter()

@router.get("/stream")
async def stream_events(request: Request):
    """
    Server-Sent Events (SSE) endpoint.
    Maintains a persistent connection to stream events to the frontend.
    """
    async def event_generator():
        queue = await event_bus.subscribe()
        try:
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break
                
                try:
                    # Wait for event with timeout to allow ping/check disconnect
                    event: EventBase = await asyncio.wait_for(queue.get(), timeout=15.0)
                    
                    # SEE Format: "data: <json>\n\n"
                    # We can also use "event: <type>\n" if we want named events
                    yield f"event: {event.type}\n"
                    yield f"data: {event.model_dump_json()}\n\n"
                    
                except asyncio.TimeoutError:
                    # Send ping to keep connection alive
                    yield f"event: ping\n"
                    yield f"data: {{ \"timestamp\": \"{datetime.utcnow().isoformat()}\" }}\n\n"
                    
        finally:
            event_bus.unsubscribe(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

from datetime import datetime
