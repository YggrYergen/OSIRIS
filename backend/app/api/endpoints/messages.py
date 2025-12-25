from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api import deps
from app.models.message import Message
from app.models.user import User

router = APIRouter()

@router.get("/{task_id}", response_model=List[Any])
async def read_messages(
    task_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get all messages for a specific task.
    """
    result = await db.execute(select(Message).where(Message.task_id == task_id).order_by(Message.timestamp))
    messages = result.scalars().all()
    return messages
