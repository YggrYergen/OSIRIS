from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base_class import Base
import enum

class SenderType(str, enum.Enum):
    USER = "user"
    SYSTEM = "system"
    AGENT = "agent"
    SUPERVISOR = "supervisor"

class Message(Base):
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id"), nullable=False)
    task = relationship("Task")

    sender_type = Column(Enum(SenderType), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
