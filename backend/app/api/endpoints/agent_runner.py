from typing import Dict, Any
from fastapi import APIRouter, Body, BackgroundTasks
from app.services.agent_service import AgentService
from app.services.brain.factory import BrainProvider

router = APIRouter()

@router.post("/run/{task_id}")
async def run_agent(task_id: int, background_tasks: BackgroundTasks, payload: Dict[str, Any] = Body(...)):
    """
    Trigger the agent to run on a specific task.
    """
    instruction = payload.get("instruction", "Continue working.")
    provider_str = payload.get("provider", "openai")
    
    # Map string to Enum
    try:
        provider = BrainProvider(provider_str)
    except ValueError:
        provider = BrainProvider.OPENAI

    agent = AgentService(task_id=task_id, provider=provider)
    
    # Run in background to not block request
    background_tasks.add_task(agent.run_step, instruction, [])
    
    return {"status": "started", "task_id": task_id, "brain": provider}
