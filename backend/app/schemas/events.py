from enum import Enum
from typing import Any, Optional, Dict
from pydantic import BaseModel
from datetime import datetime

class EventType(str, Enum):
    TASK_UPDATE = "task_update"       # Status changes
    NEW_MESSAGE = "new_message"       # Chat messages
    ARTIFACT_UPDATE = "artifact_update" # Code/File changes
    TERMINAL_LOG = "terminal_log"     # Command outputs
    SYSTEM_ALERT = "system_alert"     # Global notifications
    PING = "ping"                     # Keep alive

class EventBase(BaseModel):
    type: EventType
    timestamp: datetime = datetime.utcnow()
    task_id: Optional[int] = None     # If event is specific to a task

class EventMessage(EventBase):
    type: EventType = EventType.NEW_MESSAGE
    data: Dict[str, Any] # Contains content, sender, etc.

class EventTaskUpdate(EventBase):
    type: EventType = EventType.TASK_UPDATE
    data: Dict[str, Any] # Contains old_status, new_status

class EventLog(EventBase):
    type: EventType = EventType.TERMINAL_LOG
    data: Dict[str, Any] # Contains output, command

class EventArtifact(EventBase):
    type: EventType = EventType.ARTIFACT_UPDATE
    data: Dict[str, Any] # Contains filename, diff or content
