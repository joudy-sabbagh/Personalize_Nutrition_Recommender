# RUN: uvicorn app:app --host 0.0.0.0 --port 8004
from fastapi import FastAPI, File, UploadFile, Form
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import joblib
import os
import boto3
from io import StringIO
import json

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
        return pd.read_csv(StringIO(response['Body'].read().decode('utf-8')))
    except Exception as e:
        print(f"Error loading data from S3: {str(e)}")
        # Fallback to local if available (for development)
        if os.path.exists(file_key):
            return pd.read_csv(file_key)
        else:
            raise e

# === Load top microbiome features from S3 ===
bucket_name = os.environ.get('S3_BUCKET_NAME', 'nutritiondataset')
top_bacteria_path = "Dataset/top_bacteria_union.csv"
try:
    top_bacteria_df = load_data_from_s3(bucket_name, top_bacteria_path)
    top_bacteria = top_bacteria_df["bacteria"].tolist()
except Exception as e:
    print(f"Warning: Could not load bacteria data from S3: {str(e)}")
    # Fallback paths for local development
    local_paths = [
        "Data-Processing/Dataset/top_bacteria_union.csv",
        "../Data-Processing/Dataset/top_bacteria_union.csv"
    ]
    for path in local_paths:
        if os.path.exists(path):
            top_bacteria = pd.read_csv(path)["bacteria"].tolist()
            break
    else:
        top_bacteria = []  # Empty list as last resort

# === Load local trained model ===
model = joblib.load("glucose_predictor_local.pkl")

@app.post("/predict-glucose")
async def predict_glucose(
    bio_file: UploadFile = File(...),
    micro_file: UploadFile = File(...),
    protein_pct: float = Form(...),
    fat_pct: float = Form(...),
    carbs_pct: float = Form(...),
    sugar_risk: int = Form(...),
    refined_carb: int = Form(...),
    meal_category: str = Form(...)
):
    # === Load clinical data from file ===
    bio_df = pd.read_csv(bio_file.file)

    # Rename columns to match training data
    bio_df = bio_df.rename(columns={
        'Age': 'clinical_Age',
        'BMI': 'clinical_BMI',
        'Fasting GLU - PDL (Lab)': 'clinical_fasting_glucose',
        'Insulin ': 'clinical_fasting_insulin',
        'A1c PDL (Lab)': 'clinical_HbA1c',
        'Gender': 'clinical_Gender'
    })

    # Compute HOMA-IR
    bio_df["clinical_HOMA_IR"] = (
        bio_df["clinical_fasting_glucose"] * bio_df["clinical_fasting_insulin"]
    ) / 405
    clinical_cols = [
        "clinical_Age", "clinical_BMI", "clinical_fasting_glucose", 
        "clinical_fasting_insulin", "clinical_HbA1c", "clinical_HOMA_IR", "clinical_Gender"
    ]
    clinical_row = bio_df[clinical_cols].iloc[0].to_dict()

    # Normalize numerical clinical fields
    numerical_cols = [k for k in clinical_row if k.startswith("clinical_") and k != "clinical_Gender"]
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(pd.DataFrame([clinical_row])[numerical_cols])
    for i, col in enumerate(numerical_cols):
        clinical_row[col] = scaled[0][i]

    # === Load and process microbiome ===
    micro_df = pd.read_csv(micro_file.file).drop(columns=["subject"], errors="ignore")
    for col in top_bacteria:
        if col not in micro_df.columns:
            micro_df[col] = 0
    micro_row = micro_df[top_bacteria].iloc[0].to_dict()

    # === Combine everything ===
    input_row = {
        "protein_pct": protein_pct,
        "fat_pct": fat_pct,
        "carbs_pct": carbs_pct,
        "sugar_risk": sugar_risk,
        "refined_carb": refined_carb,
        "meal_category": meal_category.lower(),
        **clinical_row,
        **micro_row
    }

    input_df = pd.DataFrame([input_row])

    # Align with training features
    for col in model.feature_names_in_:
        if col not in input_df.columns:
            input_df[col] = 0
    input_aligned = input_df[model.feature_names_in_]

    # Predict
    prediction = model.predict(input_aligned)[0]
    spike_60 = round(float(prediction), 2)

    message = "This food is likely to increase your glucose levels." if spike_60 > 30 else \
              "This food appears to be safe for your glucose response."

    return {
        "glucose_spike_60min": spike_60,
        "message": message
    }
