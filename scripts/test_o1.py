
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.services.brain.openai_brain import OpenAIBrain

async def test_o1_brain():
    print(f"Testing OpenAI o1-mini logic...")
    
    # Intentionally use a system message to verify it gets remapped/handled
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Solve 2+2"}
    ]
    
    brain = OpenAIBrain(model="o1-mini")
    
    print(f"Sending request to OpenAI with model {brain.model_name}...")
    try:
        response = await brain.think(messages)
        print("\n--- RESPONSE RECEIVED ---")
        print(response)
    except Exception as e:
        print("\n--- ERROR ---")
        print(f"Type: {type(e)}")
        print(f"Message: {e}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_o1_brain())
