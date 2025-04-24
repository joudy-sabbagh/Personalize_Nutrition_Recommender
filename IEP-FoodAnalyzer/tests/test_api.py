import pytest
from httpx import AsyncClient, ASGITransport
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import app

TEST_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "test.jpg")  # match your uploaded image name

@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_generate_labels():
    if not os.path.exists(TEST_IMAGE_PATH):
        pytest.skip("Test image not available")

    with open(TEST_IMAGE_PATH, "rb") as f:
        image_data = f.read()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        files = {"image": ("test.jpg", image_data, "image/jpg")}
        response = await ac.post("/generate-labels", files=files)

    # Either a valid result or a Clarifai API fallback
    assert response.status_code in [200, 502]
    if response.status_code == 200:
        assert "labels" in response.json()
