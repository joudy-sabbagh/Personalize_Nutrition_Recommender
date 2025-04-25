import pytest
from httpx import AsyncClient, ASGITransport
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import app

TEST_BIO = os.path.join(os.path.dirname(__file__), "test_bio.csv")
TEST_MICRO = os.path.join(os.path.dirname(__file__), "test_microbe.csv")

@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_predict_glucose():
    if not (os.path.exists(TEST_BIO) and os.path.exists(TEST_MICRO)):
        pytest.skip("CSV test files not available")

    with open(TEST_BIO, "rb") as bio, open(TEST_MICRO, "rb") as micro:
        form_data = {
            "protein_pct": "30",
            "fat_pct": "25",
            "carbs_pct": "45",
            "sugar_risk": "1",
            "refined_carb": "0",
            "meal_category": "Lunch",
        }
        files = {
            "bio_file": ("bio.csv", bio, "text/csv"),
            "micro_file": ("micro.csv", micro, "text/csv")
        }

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/predict-glucose", data=form_data, files=files)

    assert response.status_code == 200
    assert "glucose_spike_60min" in response.json()
