# uvicorn app:app --reload --port 8003

from fastapi import FastAPI, File, UploadFile
import pandas as pd
import joblib
import re
from sklearn.preprocessing import StandardScaler
from io import StringIO, BytesIO
import os
import boto3

app = FastAPI()

def load_data_from_s3(bucket_name, file_key):
    """Load data from S3 bucket"""
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_DEFAULT_REGION', 'eu-north-1')
    )
    
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        return response['Body'].read()
    except Exception as e:
        print(f"Error loading data from S3: {str(e)}")
        return None

def load_model_and_features(model_path):
    """Load model from S3 or local path"""
    # Try S3 first
    bucket_name = os.environ.get('S3_BUCKET_NAME')
    if bucket_name:
        try:
            model_bytes = load_data_from_s3(bucket_name, f"Dataset/{model_path}")
            if model_bytes:
                model_data = joblib.load(BytesIO(model_bytes))
                if isinstance(model_data, dict):
                    return (
                        model_data['model'],
                        model_data['features'],
                        model_data.get('scaler', StandardScaler())
                    )
        except Exception as e:
            print(f"S3 model loading failed: {str(e)}. Trying local file.")
    
    # Fallback to local file
    try:
        model_data = joblib.load(model_path)
        if isinstance(model_data, dict):
            return (
                model_data['model'],
                model_data['features'],
                model_data.get('scaler', StandardScaler())
            )
        else:
            raise ValueError("Model missing feature metadata.")
    except Exception as e:
        print(f"Local model loading failed: {str(e)}")
        raise ValueError(f"Could not load model from any source: {str(e)}")

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
    
@app.get("/health")
def health_check():
    return {"status": "ok"}
