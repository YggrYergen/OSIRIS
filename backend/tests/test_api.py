import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_task_via_webhook(client: AsyncClient):
    payload = {"from": "5491100000000", "text": "Necesito una landing page para ayer"}
    response = await client.post("/api/v1/webhooks/whatsapp", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "received"
    assert "task_id" in data

@pytest.mark.asyncio
async def test_read_tasks(client: AsyncClient):
    # First create a task
    await client.post("/api/v1/webhooks/whatsapp", json={"from": "123", "text": "Test Task"})
    
    # Read tasks
    response = await client.get("/api/v1/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["description"] == "Test Task"
