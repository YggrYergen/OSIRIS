from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.task import TaskStatus, TaskSource

class TaskBase(BaseModel):
    title: Optional[str] = None
    description: str
    source: TaskSource = TaskSource.WEB_CHAT
    created_by: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    assigned_to: Optional[int] = None

class TaskInDBBase(TaskBase):
    id: int
    status: TaskStatus
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Task(TaskInDBBase):
    pass
