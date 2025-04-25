# RUN: uvicorn app:app --reload --port 8001

import os
import base64
from tempfile import NamedTemporaryFile
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from prometheus_client import make_asgi_app, Counter, Summary, Gauge

# === Monitoring Metrics ===
REQUEST_COUNT = Counter("food_analyzer_request_count", "Total number of requests to Food Analyzer")
REQUEST_LATENCY = Summary("food_analyzer_request_latency_seconds", "Request latency in seconds")
LAST_LABEL_CONFIDENCE = Gauge("food_analyzer_last_label_confidence", "Confidence score of the last label predicted")

# === Load Environment Variables ===
load_dotenv()  
CLARIFAI_PAT      = os.getenv("CLARIFAI_PAT")
CLARIFAI_USER_ID  = os.getenv("CLARIFAI_USER_ID")
CLARIFAI_APP_ID   = os.getenv("CLARIFAI_APP_ID")

if not CLARIFAI_PAT or not CLARIFAI_USER_ID or not CLARIFAI_APP_ID:
    raise RuntimeError(
        "Missing Clarifai credentials in .env. "
        "Ensure CLARIFAI_PAT, CLARIFAI_USER_ID, and CLARIFAI_APP_ID are set."
    )

# === Clarifai Model Configuration ===
MODEL_ID         = "food-item-recognition"
MODEL_VERSION_ID = "1d5fd481e0cf4826aa72ec3ff049e044"
API_URL = (
    f"https://api.clarifai.com/v2/models/{MODEL_ID}"
    f"/versions/{MODEL_VERSION_ID}/outputs"
)

# === FastAPI App Setup ===
app = FastAPI(title="IEP-FoodAnalyzer")

# CORS for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Mount /metrics for Prometheus
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Middleware to track request counts and latencies
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    REQUEST_COUNT.inc()
    start_time = time.time()
    response = await call_next(request)
    REQUEST_LATENCY.observe(time.time() - start_time)
    return response

# === API Endpoints ===

@app.post("/generate-labels")
async def generate_labels(image: UploadFile = File(...)):
    """Uploads image to Clarifai API and returns detected food labels."""
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")

    with NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(await image.read())
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode()

        payload = {
            "user_app_id": {
                "user_id": CLARIFAI_USER_ID,
                "app_id":  CLARIFAI_APP_ID
            },
            "inputs": [
                { "data": { "image": { "base64": b64_data } } }
            ]
        }
        headers = {
            "Authorization": f"Key {CLARIFAI_PAT}",
            "Content-Type":  "application/json"
        }

        resp = requests.post(API_URL, headers=headers, json=payload)
        resp.raise_for_status()

        outputs  = resp.json().get("outputs", [])
        if not outputs:
            return JSONResponse(status_code=502, content={"error": "No output from Clarifai"})

        concepts = outputs[0]["data"].get("concepts", [])
        labels = [
            {"name": c["name"], "confidence": round(c["value"] * 100, 2)}
            for c in concepts
        ]

        # === Monitor last label confidence ===
        if labels:
            LAST_LABEL_CONFIDENCE.set(labels[0]["confidence"])

        return {"labels": labels}

    except requests.HTTPError as http_err:
        return JSONResponse(status_code=http_err.response.status_code, content=http_err.response.json())
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

@app.get("/health")
def health_check():
    return {"status": "ok"}