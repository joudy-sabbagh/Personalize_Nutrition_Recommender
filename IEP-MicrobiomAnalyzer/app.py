# uvicorn app:app --reload --port 8003

from fastapi import FastAPI, File, UploadFile, Request
import pandas as pd
import joblib
import re
from sklearn.preprocessing import StandardScaler
from io import StringIO, BytesIO
import os
import time

from prometheus_client import make_asgi_app, Counter, Summary, Gauge

# === Monitoring Metrics ===
REQUEST_COUNT = Counter("microbiom_analyzer_request_count", "Total number of requests to Microbiom Analyzer")
REQUEST_LATENCY = Summary("microbiom_analyzer_request_latency_seconds", "Request latency in seconds")
LAST_GUT_HEALTH_PROB = Gauge("microbiom_analyzer_last_gut_health_probability", "Last predicted gut health probability")

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

# Load model data once at startup
try:
    model_data = joblib.load("microbiome_model.pkl")
    model = model_data['model']
    feature_cols = model_data['features']
    scaler = model_data.get('scaler', StandardScaler())
except Exception as e:
    raise RuntimeError(f"Failed to load model: {str(e)}")

@app.post("/predict-gut-health-file")
async def predict_gut_health(file: UploadFile = File(...)):
    try:
        # Read and parse the CSV file
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode("utf-8")))
        
        # Clean column names by removing special characters
        df.columns = [re.sub(r'[\[\],<>]', '', col).strip() for col in df.columns.astype(str)]
        
        # Check for required features
        missing = set(feature_cols) - set(df.columns)
        if missing:
            return {"error": f"Missing required features: {missing}"}

        # Prepare and scale features
        X = df[feature_cols]
        X_scaled = scaler.transform(X) if scaler else X

        # Make prediction
        prob = model.predict_proba(X_scaled)[0, 1]
        
        return {
            "probability": round(float(prob), 3),
            "prediction": "Good" if prob > 0.5 else "Bad"
        }

    except pd.errors.EmptyDataError:
        return {"error": "Uploaded file is empty or invalid"}
    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}
    
@app.get("/health")
def health_check():
    return {"status": "ok"}