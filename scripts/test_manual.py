import sys
import os
import asyncio
# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.logging_config import setup_logging, log
from app.models.task import Task, TaskStatus
from app.db.base import Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Mock DB
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

async def main():
    setup_logging("INFO")
    log.info("Starting manual verification script")
    
    try:
        engine = create_async_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args={"check_same_thread": False},
        )
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        log.info("Tables created in memory DB")

        # Test Insert
        async with async_session() as session:
            new_task = Task(title="Manual Test", description="Testing without Pytest")
            session.add(new_task)
            await session.commit()
            await session.refresh(new_task)
            log.info(f"Task created: {new_task.id} - {new_task.title}")
            
            # Verify Status Default
            assert new_task.status == TaskStatus.PENDING
            log.success("Task status verification passed")

    except Exception as e:
        log.exception("Validation script failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
