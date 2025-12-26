
import requests
import json

def test_run_endpoint():
    print("Testing /api/v1/agent/run/2 ...")
    url = "http://localhost:8000/api/v1/agent/run/2"
    payload = {
        "instruction": "Say hello from script",
        "provider": "openai",
        "model": "gpt-4o"
    }
    
    try:
        res = requests.post(url, json=payload)
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_run_endpoint()
