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
        # Convert generic tool definitions to OpenAI format if needed
        
        final_messages = messages
        api_kwargs = {
            "model": self._model,
            "messages": final_messages,
        }

        if self._model.startswith("o1-"):
            # o1 models (Dec 2024+) use 'developer' role instead of 'system'.
            # They support tools now.
            cleaned_messages = []
            for msg in messages:
                role = msg["role"]
                if role == "system":
                    role = "developer" # Remap system to developer for o1
                cleaned_messages.append({"role": role, "content": msg["content"]})
            api_kwargs["messages"] = cleaned_messages
        else:
            # Standard GPT-4o behavior
            pass

        if tools:
            api_kwargs["tools"] = tools

        print(f"DEBUG: Calling OpenAI with model={self._model}, tools_count={len(tools) if tools else 0}")
        
        try:
            response = await self.client.chat.completions.create(**api_kwargs)
        except Exception as e:
            print(f"ERROR calling OpenAI: {e}")
            raise e
        
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
