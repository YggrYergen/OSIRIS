import requests
import json
import time

URL = "http://localhost:8000/api/v1/webhooks/whatsapp"

def send_task(text, sender="Human Tester"):
    payload = {
        "from": sender,
        "text": text
    }
    print(f"Sending webhook: {text}...")
    try:
        res = requests.post(URL, json=payload)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("--- INYECTOR DE TAREAS WHATSAPP (SIMULADO) ---")
    task_desc = input("Describe la tarea (ej: 'Crear Landing Page estilo Cyberpunk'): ")
    if not task_desc:
        task_desc = "Crear Landing Page estilo Cyberpunk con Next.js y Tailwind"
    
    send_task(task_desc)
