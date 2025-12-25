from app.services.brain.base import BrainInterface
from app.services.brain.openai_brain import OpenAIBrain
from app.services.brain.gemini_brain import GeminiBrain
from enum import Enum

class BrainProvider(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"

class BrainFactory:
    _instances: dict = {}

    @staticmethod
    def get_brain(provider: BrainProvider, model: str = None) -> BrainInterface:
        """
        Returns a brain instance. Could be cached per provider configuration.
        """
        key = f"{provider}:{model}"
        if key in BrainFactory._instances:
            return BrainFactory._instances[key]
        
        if provider == BrainProvider.OPENAI:
            instance = OpenAIBrain(model=model or "gpt-4o")
        elif provider == BrainProvider.GEMINI:
            instance = GeminiBrain(model=model or "gemini-1.5-pro")
        else:
            raise ValueError(f"Unknown provider: {provider}")
            
        BrainFactory._instances[key] = instance
        return instance
