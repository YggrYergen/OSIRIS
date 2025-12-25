import requests
import time
import json

BASE_URL = "http://localhost:8000/api/v1/webhooks/ingest/simulation"

TASK_ID = 2

def send(event_type, data):
    payload = {
        "type": event_type,
        "task_id": TASK_ID,
        "data": data
    }
    print(f"Sending {event_type}...")
    try:
        res = requests.post(BASE_URL, json=payload)
        print(f"Status: {res.status_code}")
    except Exception as e:
        print(f"Failed: {e}")

def run_simulation():
    print("Starting Agent Simulation...")
    
    # 1. Agent Thought
    send("new_message", {
        "content": "Entendido. Voy a crear el archivo 'simulation.py' y luego lo ejecutaré.",
        "sender": "Agent Smith",
        "sender_type": "agent"
    })
    time.sleep(2)
    
    # 2. Writing File (Progressive)
    code_content = "import time\n"
    send("artifact_update", {"filename": "simulation.py", "content": code_content})
    time.sleep(0.5)
    
    code_content += "print('Iniciando proceso nuclear...')\n"
    send("artifact_update", {"filename": "simulation.py", "content": code_content})
    time.sleep(0.5)

    code_content += "for i in range(5):\n    print(f'Countdown: {5-i}')\n    time.sleep(0.2)\n"
    send("artifact_update", {"filename": "simulation.py", "content": code_content})
    time.sleep(1)

    code_content += "print('BOOM! 💥')"
    send("artifact_update", {"filename": "simulation.py", "content": code_content})
    time.sleep(2)

    # 3. Log Output
    send("terminal_log", {"command": "python simulation.py", "output": "Iniciando proceso nuclear..."})
    time.sleep(1)
    
    for i in range(5):
        send("terminal_log", {"command": "", "output": f"Countdown: {5-i}"})
        time.sleep(0.5)
        
    send("terminal_log", {"command": "", "output": "BOOM! 💥"})

    print("Simulation Complete.")

if __name__ == "__main__":
    run_simulation()
