# uvicorn app:app --reload --port 8003
from fastapi import FastAPI, File, UploadFile
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from io import StringIO
import re

app = FastAPI()

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