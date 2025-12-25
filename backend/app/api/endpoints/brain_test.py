from typing import Any, Dict
from fastapi import APIRouter, Body
from app.services.brain.factory import BrainFactory, BrainProvider

router = APIRouter()

@router.post("/test/brain")
async def test_brain(provider: str = "openai", message: str = "Hello"):
    """
    Test endpoint to verify Brain Factory switching.
    """
    try:
        brain_provider = BrainProvider(provider)
        brain = BrainFactory.get_brain(brain_provider)
        
        # Determine current model name
        model_name = brain.model_name
        
        # Simulate simple thought (Mocked for safety if keys missing)
        # result = await brain.think([{"role": "user", "content": message}])
        
        return {
            "status": "success",
            "provider": provider,
            "model_used": model_name,
            "message_received": message,
            "note": "Actual LLM call commented out for safety in this test step."
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}
