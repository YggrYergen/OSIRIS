from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api import deps
from app.models.task import Task
from app.models.user import User
from app.schemas import task as task_schema

router = APIRouter()

@router.get("/", response_model=List[task_schema.Task])
async def read_tasks(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve tasks. (Requires Authentication)
    """
    result = await db.execute(select(Task).offset(skip).limit(limit))
    tasks = result.scalars().all()
    return tasks

@router.post("/", response_model=task_schema.Task)
async def create_task(
    *,
    db: AsyncSession = Depends(deps.get_db),
    task_in: task_schema.TaskCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new task. (Requires Authentication)
    """
    task = Task(**task_in.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

@router.get("/{id}", response_model=task_schema.Task)
async def read_task_by_id(
    id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get a specific task by ID.
    """
    result = await db.execute(select(Task).where(Task.id == id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return task
