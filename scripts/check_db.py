
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import AsyncSessionLocal
from app.models.message import Message
from sqlalchemy import select

async def check_messages(task_id: int):
    print(f"Checking DB messages for Task {task_id}...")
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Message).where(Message.task_id == task_id).order_by(Message.timestamp)
        )
        messages = result.scalars().all()
        
        print(f"--- Found {len(messages)} messages ---")
        for m in messages:
            print(f"[{m.timestamp}] {m.sender_type}: {m.content[:50]}...")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_messages(2))
