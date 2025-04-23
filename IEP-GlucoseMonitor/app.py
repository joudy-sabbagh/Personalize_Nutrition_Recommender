# RUN: uvicorn app:app --host 0.0.0.0 --port 8004
from fastapi import FastAPI, File, UploadFile, Form
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import joblib

app = FastAPI()

# === Load top microbiome features ===
top_bacteria = pd.read_csv("../Data-Processing/Dataset/top_bacteria_union.csv")["bacteria"].tolist()

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
