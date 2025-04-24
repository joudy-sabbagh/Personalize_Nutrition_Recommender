import pytest
from httpx import AsyncClient, ASGITransport
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import app

TEST_MICROBIOME_FILE = os.path.join(os.path.dirname(__file__), "test_microbe.csv")

@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_predict_gut_health_file():
    if not os.path.exists(TEST_MICROBIOME_FILE):
        pytest.skip("Microbiome test file not found.")

    with open(TEST_MICROBIOME_FILE, "rb") as file:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            files = {"file": ("micro.csv", file, "text/csv")}
            response = await ac.post("/predict-gut-health-file", files=files)

    assert response.status_code == 200
    json_data = response.json()
    assert "prediction" in json_data or "error" in json_data
