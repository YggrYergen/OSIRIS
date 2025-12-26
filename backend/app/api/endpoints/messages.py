from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api import deps
from app.models.message import Message
from app.models.user import User

router = APIRouter()

@router.get("/{task_id}", response_model=List[Dict[str, Any]])
async def read_messages(
    task_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get all messages for a specific task.
    """
    try:
        result = await db.execute(select(Message).where(Message.task_id == task_id).order_by(Message.timestamp))
        messages = result.scalars().all()
        
        serialized = []
        for m in messages:
            # Force serialization of Enum to string
            sender_type_str = m.sender_type.value if hasattr(m.sender_type, "value") else str(m.sender_type)
            
            serialized.append({
                "id": m.id,
                "task_id": m.task_id,
                "sender_type": sender_type_str,
                "content": m.content,
                "timestamp": m.timestamp
            })
            
        print(f"DEBUG API: Serialized {len(serialized)} messages. Sample sender_type: {serialized[-1]['sender_type'] if serialized else 'N/A'}")
        return serialized
    except Exception as e:
        print(f"DEBUG ERROR in read_messages: {e}")
        raise e
