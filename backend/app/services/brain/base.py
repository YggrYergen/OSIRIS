from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BrainInterface(ABC):
    """
    Abstract Base Class for AI Brains (OpenAI, Gemini, LocalLLM, etc.)
    """
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        pass

    @abstractmethod
    async def think(self, 
                    messages: List[Dict[str, str]], 
                    tools: Optional[List[Any]] = None) -> Dict[str, Any]:
        """
        Process the conversation history and return a decision/action.
        
        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
            tools: List of tool definitions available to the agent.
            
        Returns:
            Dict containing:
            - 'content': The text response (if any)
            - 'tool_calls': List of tool invocations (if any)
            - 'usage': Token usage stats (optional)
        """
        pass
