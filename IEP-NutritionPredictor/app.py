# RUN: uvicorn app:app --host 0.0.0.0 --port 8002

from fastapi import FastAPI, Request
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv
import re
import time

from prometheus_client import make_asgi_app, Counter, Summary, Gauge

# === Monitoring Metrics ===
REQUEST_COUNT = Counter("nutrition_predictor_request_count", "Total number of prediction requests to Nutrition Predictor")
REQUEST_LATENCY = Summary("nutrition_predictor_request_latency_seconds", "Prediction request latency in seconds")
LAST_PREDICTED_CARBS = Gauge("nutrition_predictor_last_predicted_carbs_pct", "Last predicted carbohydrates percentage")

# === Load API Key ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# === FastAPI App Setup ===
app = FastAPI()

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

class FoodDescription(BaseModel):
    caption: str

@app.post("/predict-nutrition")
def predict_nutrition(payload: FoodDescription):
    caption = payload.caption
    prompt = f"""
        You are a nutrition expert. Given the following food description, estimate the approximate macronutrient distribution of the meal:

        Return:
        - protein_pct = percentage of total macronutrients that is protein (0–100)
        - fat_pct = percentage of total macronutrients that is fat (0–100)
        - carbs_pct = percentage of total macronutrients that is carbohydrates (0–100)
        - sugar_risk = 1 if the food likely contains added sugar or naturally high sugar, else 0
        - refined_carb = 1 if the food includes refined carbs (e.g., white pasta, white bread), else 0

        Assume the description includes visible ingredients, portion hints, and preparation (e.g., “with olive oil”, “large serving”). If no portion is provided, guess reasonably.

        Format your output like this:
        [protein_pct = , fat_pct = , carbs_pct = , sugar_risk = , refined_carb = ]

        Food description: {caption}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a nutrition expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        result = response['choices'][0]['message']['content'].strip()
        result = result.replace("[", "").replace("]", "")

        def extract_pct(label):
            match = re.search(rf"{label}\s*=\s*(\d+)", result)
            return int(match.group(1)) if match else -1 

        def extract_binary(label):
            match = re.search(rf"{label}\s*=\s*(1|0)", result)
            return int(match.group(1)) if match else -1

        # Extract nutrition values
        nutrition = {
            "protein_pct": extract_pct("protein_pct"),
            "fat_pct": extract_pct("fat_pct"),
            "carbs_pct": extract_pct("carbs_pct"),
            "sugar_risk": extract_binary("sugar_risk"),
            "refined_carb": extract_binary("refined_carb")
        }

        # === Update Prometheus Metric ===
        if nutrition["carbs_pct"] != -1:
            LAST_PREDICTED_CARBS.set(nutrition["carbs_pct"])

        return {
            "nutrition": nutrition,
            "result": result
        }

    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
def health_check():
    return {"status": "ok"}