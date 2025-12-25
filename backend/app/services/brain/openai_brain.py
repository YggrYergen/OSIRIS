from openai import AsyncOpenAI
from app.services.brain.base import BrainInterface
from app.core.config import settings
from typing import List, Dict, Any, Optional
import json

class OpenAIBrain(BrainInterface):
    def __init__(self, model: str = "gpt-4o"):
        self._model = model
        # Assuming you have OPENAI_API_KEY in settings or env
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    @property
    def model_name(self) -> str:
        return f"OpenAI ({self._model})"

    async def think(self, messages: List[Dict[str, str]], tools: Optional[List[Any]] = None) -> Dict[str, Any]:
        # Convert our generic tool definitions to OpenAI format if needed
        # For this phase, we assume tools are passed in a compatible format or we handle conversion here.
        
        response = await self.client.chat.completions.create(
            model=self._model,
            messages=messages,
            tools=tools
        )
        
        choice = response.choices[0]
        message = choice.message
        
        tool_calls = []
        if message.tool_calls:
            for tc in message.tool_calls:
                tool_calls.append({
                    "id": tc.id,
                    "function": tc.function.name,
                    "arguments": json.loads(tc.function.arguments)
                })

        return {
            "content": message.content,
            "tool_calls": tool_calls,
            "usage": response.usage.model_dump() if response.usage else {}
        }
