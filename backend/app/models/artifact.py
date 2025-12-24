from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base_class import Base
import enum

class ArtifactType(str, enum.Enum):
    CODE = "code"
    TEXT = "text"
    SCREENSHOT = "screenshot"
    DIFF = "diff"

class ArtifactStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Artifact(Base):
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id"), nullable=False)
    task = relationship("Task")

    type = Column(Enum(ArtifactType), nullable=False)
    content = Column(Text, nullable=False) # Can be path or content
    status = Column(Enum(ArtifactStatus), default=ArtifactStatus.PENDING)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
