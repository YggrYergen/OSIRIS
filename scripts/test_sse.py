import requests
import json

def listen():
    url = "http://localhost:8000/api/v1/stream"
    print(f"Connecting to SSE {url}...")
    
    with requests.get(url, stream=True) as response:
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                print(f"Received: {decoded_line}")

if __name__ == "__main__":
    listen()
