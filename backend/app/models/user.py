from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.sql import func
from app.models.base_class import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    AGENT = "agent"

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.AGENT, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
