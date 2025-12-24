from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base_class import Base
import enum

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    CLAIMED = "claimed"
    IN_PROGRESS = "in_progress"
    REVIEW_PENDING = "review_pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DONE = "done"

class TaskSource(str, enum.Enum):
    WHATSAPP = "whatsapp"
    WEB_CHAT = "web_chat"
    FORM = "form"

class Task(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    source = Column(Enum(TaskSource), default=TaskSource.WEB_CHAT)
    created_by = Column(String) # External identifier (e.g. phone number)
    
    assigned_to = Column(Integer, ForeignKey("user.id"), nullable=True)
    assigned_user = relationship("User")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
