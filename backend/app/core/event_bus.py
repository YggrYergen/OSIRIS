import asyncio
from typing import List, Dict, Optional
from app.schemas.events import EventBase, EventType
import logging

class EventBus:
    def __init__(self):
        # We store list of queues for connected clients
        # In a scaled app, this would be Redis Pub/Sub
        self.subscribers: List[asyncio.Queue] = []
        self._logger = logging.getLogger("event_bus")

    async def subscribe(self) -> asyncio.Queue:
        """
        Creates a new queue for a client connection.
        """
        queue = asyncio.Queue()
        self.subscribers.append(queue)
        self._logger.debug(f"Client subscribed. Total subscribers: {len(self.subscribers)}")
        return queue

    def unsubscribe(self, queue: asyncio.Queue):
        if queue in self.subscribers:
            self.subscribers.remove(queue)
            self._logger.debug(f"Client unsubscribed. Total subscribers: {len(self.subscribers)}")

    async def publish(self, event: EventBase):
        """
        Broadcast event to all subscribers.
        Filtering by task_id happens at the client level or could be optimized here.
        For Phase 2, we broadcast all to all (dashboard needs updates, task detail needs updates).
        """
        # Convert to dict once
        payload = event.model_dump_json()
        
        # We wrap in SSE format here or in the endpoint? 
        # Usually easier to push the object and let endpoint format it.
        
        to_remove = []
        for q in self.subscribers:
            try:
                # Put non-blocking
                q.put_nowait(event)
            except asyncio.QueueFull:
                self._logger.warning("Subscriber queue full, dropping client")
                to_remove.append(q)
        
        for q in to_remove:
            self.unsubscribe(q)

# Global Singleton
event_bus = EventBus()
