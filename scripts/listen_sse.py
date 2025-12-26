
import requests
import json
import sys

def listen_sse():
    print("Listening to SSE stream at http://localhost:8000/api/v1/stream ...")
    try:
        with requests.get("http://localhost:8000/api/v1/stream", stream=True) as response:
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith("data: "):
                        print(f"EVENT RECEIVED: {decoded}")
    except KeyboardInterrupt:
        print("Stopping listener.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    listen_sse()
