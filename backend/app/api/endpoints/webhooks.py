from typing import Any, Dict
from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.models.task import Task, TaskSource, TaskStatus
from app.schemas.task import TaskCreate

from app.core.logging_config import log

router = APIRouter()

@router.post("/whatsapp")
async def whatsapp_webhook(
    payload: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Receive WhatsApp webhook.
    Expected payload: {"from": "12345", "text": "Task description"}
    """
    log.debug(f"Received webhook payload: {payload}")
    
    # Simple adapter logic
    text = payload.get("text", "")
    sender = payload.get("from", "unknown")
    
    if not text:
        log.warning("Webhook payload missing 'text' field. Ignoring.")
        return {"status": "ignored", "reason": "no text"}

    task_in = TaskCreate(
        title=text[:50] + "...",
        description=text,
        source=TaskSource.WHATSAPP,
        created_by=sender
    )
    
    task = Task(**task_in.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    return {"status": "received", "task_id": task.id}
