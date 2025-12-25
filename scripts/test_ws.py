import asyncio
import websockets
import json

async def hello():
    uri = "ws://127.0.0.1:8000/api/v1/ws/tasks/2"
    print(f"Connecting to {uri} with Origin http://localhost:3000...")
    try:
        # Simulate Browser Origin
        async with websockets.connect(uri, origin="http://localhost:3000") as websocket:
            print("Connected!")
            
            params = {
                "content": "Hello from Origin Test",
                "sender_type": "agent"
            }
            await websocket.send(json.dumps(params))
            print("Message sent.")

            response = await websocket.recv()
            print(f"Received: {response}")
            
    except Exception as e:
        print(f"Connection Failed: {e}")

if __name__ == "__main__":
    asyncio.run(hello())
