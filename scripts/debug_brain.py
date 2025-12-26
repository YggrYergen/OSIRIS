
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.services.brain.openai_brain import OpenAIBrain

async def test_brain():
    print(f"Testing OpenAI Key ending in: ...{settings.OPENAI_API_KEY[-5:]}")
    
    brain = OpenAIBrain(model="gpt-4o")
    
    messages = [
        {"role": "user", "content": "Hello, are you working?"}
    ]
    
    print("Sending request to OpenAI...")
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
    asyncio.run(test_brain())
