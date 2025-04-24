# uvicorn app:app --reload --port 8003

from fastapi import FastAPI, File, UploadFile
import pandas as pd
import joblib
import re
from sklearn.preprocessing import StandardScaler
from io import StringIO
import os

app = FastAPI()

def load_model_and_features(model_path):
    model_data = joblib.load(model_path)
    if isinstance(model_data, dict):
        return (
            model_data['model'],
            model_data['features'],
            model_data.get('scaler', StandardScaler())
        )
    else:
        raise ValueError("Model missing feature metadata.")

def clean_column_names(df):
    raw_cols = df.columns.astype(str)
    cleaned_cols = [re.sub(r'[\[\],<>]', '', col).strip() for col in raw_cols]
    counts = {}
    final_cols = []
    for col in cleaned_cols:
        counts[col] = counts.get(col, 0)
        final_cols.append(f"{col}_{counts[col]}" if counts[col] else col)
        counts[col] += 1
    df.columns = final_cols
    return df

@app.post("/predict-gut-health-file")
async def predict_gut_health_file(file: UploadFile = File(...)):
    try:
        # Load CSV contents
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode("utf-8")))
        df = clean_column_names(df)

        # Load model, features, scaler
        MODEL_PATH = "microbiome_model.pkl"
        model, feature_cols, scaler = load_model_and_features(MODEL_PATH)

        # Check for missing features
        missing_features = set(feature_cols) - set(df.columns)
        if missing_features:
            return {"error": f"Missing features: {missing_features}"}

        # Select and scale input
        X = df[feature_cols]
        X_scaled = scaler.transform(X)

        # Predict
        prob_good = model.predict_proba(X_scaled)[0, 1]
        prediction = "Good" if prob_good > 0.5 else "Bad"

        return {
            "probability_good": round(float(prob_good), 3),
            "prediction": prediction
        }

    except Exception as e:
        return {"error": str(e)}