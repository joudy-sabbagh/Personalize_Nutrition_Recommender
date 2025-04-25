from fastapi.middleware.cors import CORSMiddleware
# RUN: uvicorn app:app --host 0.0.0.0 --port 8000

from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
import requests
import os
import time

from prometheus_client import make_asgi_app, Counter, Summary, Gauge

# === Define Metrics ===
REQUEST_COUNT = Counter("request_count", "Total number of requests")
REQUEST_LATENCY = Summary("request_latency_seconds", "Request latency")
PREDICTION_VALUE = Gauge("last_prediction_value", "Last predicted value")

# === Setup App ===
app = FastAPI()

# Mount /metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# === Example Monitoring on Endpoint ===
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    REQUEST_COUNT.inc()
    start_time = time.time()
    response = await call_next(request)
    REQUEST_LATENCY.observe(time.time() - start_time)
    return response

# Get service URLs
FOOD_ANALYZER_URL = os.environ.get('FOOD_ANALYZER_URL', 'http://localhost:8001')
NUTRITION_PREDICTOR_URL = os.environ.get('NUTRITION_PREDICTOR_URL', 'http://localhost:8002')
MICROBIOM_ANALYZER_URL = os.environ.get('MICROBIOM_ANALYZER_URL', 'http://localhost:8003')
GLUCOSE_MONITOR_URL = os.environ.get('GLUCOSE_MONITOR_URL', 'http://localhost:8004')

@app.post("/analyze-meal")
async def analyze_meal(
    image: UploadFile = File(...),
    description: str = Form(None)
):
    image_bytes = await image.read()

    caption_response = requests.post(
        f"{FOOD_ANALYZER_URL}/generate-labels",
        files={"image": ("filename.jpg", image_bytes, image.content_type)}
    )
    if caption_response.status_code != 200:
        return {"error": "Caption failed", "details": caption_response.text}
    labels = [
        label for label in caption_response.json().get("labels", [])
        if label.get("confidence", 0) >= 20
    ]
    if not labels and (not description or description.strip().lower() == "none"):
        return {
            "error": "Image not clear",
            "message": "No ingredients were confidently detected from the image. Please provide a description of the meal to improve prediction."
        }
    ingredient_caption = "A dish containing " + ", ".join([
        f"{label['name']} ({round(label['confidence'], 1)}%)"
        for label in labels
    ]) if labels else ""
    if description and description.strip().lower() != "none":
        if ingredient_caption:
            full_caption = f"{ingredient_caption}. Additional description: {description.strip()}"
        else:
            full_caption = description.strip()
    else:
        full_caption = ingredient_caption

    caption = full_caption

    nutrition_response = requests.post(
        f"{NUTRITION_PREDICTOR_URL}/predict-nutrition",
        json={"caption": caption}
    )
    if nutrition_response.status_code != 200:
        return {"error": "Nutrition failed", "details": nutrition_response.text}

    nutrition = nutrition_response.json()

    # === Set Prometheus Metric ===
    if "sugar_risk" in nutrition:
        PREDICTION_VALUE.set(nutrition.get("sugar_risk", 0))

    return {
        "nutrition": nutrition
    }

@app.post("/predict-gut-health")
def predict_gut_health(file: UploadFile = File(...)):
    csv_bytes = file.file.read()

    gut_response = requests.post(
        f"{MICROBIOM_ANALYZER_URL}/predict-gut-health-file",
        files={"file": ("subject.csv", csv_bytes, file.content_type)}
    )
    if gut_response.status_code != 200:
        return {"error": "Gut health prediction failed", "details": gut_response.text}

    gut_result = gut_response.json()

    return gut_result

@app.post("/predict-glucose-from-all")
def predict_glucose_from_all(
    image: UploadFile = File(...),
    bio_file: UploadFile = File(...),
    micro_file: UploadFile = File(...),
    meal_category: str = Form(...)
):
    try:
        image_bytes = image.file.read()
        bio_bytes = bio_file.file.read()
        micro_bytes = micro_file.file.read()

        analyze_response = requests.post(
            f"{FOOD_ANALYZER_URL}/analyze-meal",
            files={"image": ("meal.jpg", image_bytes, image.content_type)}
        )
        if analyze_response.status_code != 200:
            return {"error": "analyze-meal failed", "details": analyze_response.text}

        analyze = analyze_response.json()
        nutrition = analyze.get("nutrition", {})

        glucose_response = requests.post(
            f"{GLUCOSE_MONITOR_URL}/predict-glucose",
            data={
                "protein_pct": nutrition.get("protein_pct", 0),
                "fat_pct": nutrition.get("fat_pct", 0),
                "carbs_pct": nutrition.get("carbs_pct", 0),
                "sugar_risk": nutrition.get("sugar_risk", 0),
                "refined_carb": nutrition.get("refined_carb", 0),
                "meal_category": meal_category
            },
            files={
                "bio_file": ("bio.csv", bio_bytes, bio_file.content_type),
                "micro_file": ("micro.csv", micro_bytes, micro_file.content_type)
            }
        )

        if glucose_response.status_code != 200:
            return {"error": "glucose prediction failed", "details": glucose_response.text}

        glucose = glucose_response.json()

        # === Set Prometheus Metric ===
        if "glucose_spike_60min" in glucose:
            PREDICTION_VALUE.set(glucose.get("glucose_spike_60min", 0))

        return {
            "caption": analyze.get("caption"),
            "nutrition": nutrition,
            "glucose_prediction": glucose
        }

    except Exception as e:
        return {"error": f"Internal server error: {str(e)}"}