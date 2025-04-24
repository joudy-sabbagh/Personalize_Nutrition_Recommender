import pytest
from httpx import AsyncClient, ASGITransport
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import app

@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_predict_nutrition():
    test_caption = {
        "caption": "Grilled chicken breast with quinoa and steamed broccoli drizzled with olive oil"
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/predict-nutrition", json=test_caption)

    assert res.status_code == 200
    json_data = res.json()

    assert "nutrition" in json_data
    for key in ["protein_pct", "fat_pct", "carbs_pct", "sugar_risk", "refined_carb"]:
        assert key in json_data["nutrition"]
