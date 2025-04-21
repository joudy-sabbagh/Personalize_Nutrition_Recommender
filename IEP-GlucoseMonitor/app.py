from fastapi import FastAPI, File, UploadFile, Form
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import MinMaxScaler

app = FastAPI()

# Load models
models = {
    "glucose_spike_30min": joblib.load("glucose_spike_30min_model.joblib"),
    "glucose_spike_60min": joblib.load("glucose_spike_60min_model.joblib")
}

@app.post("/predict-glucose")
async def predict_glucose(
    bio_file: UploadFile = File(...),
    micro_file: UploadFile = File(...),
    protein: int = Form(...),
    fat: int = Form(...),
    carbs: int = Form(...),
    gut_health: str = Form(...),
    meal_category: str = Form(...)
):
    # === Load CSVs ===
    bio_df = pd.read_csv(bio_file.file).drop(columns=["subject"], errors="ignore")
    micro_df = pd.read_csv(micro_file.file).drop(columns=["subject"], errors="ignore")

    # === Preprocess clinical ===
    bio_df = bio_df.rename(columns={
        'Fasting GLU - PDL (Lab)': 'fasting_glucose',
        'Insulin ': 'fasting_insulin',
        'A1c PDL (Lab)': 'HbA1c'
    }).dropna()

    bio_df["HOMA_IR"] = (bio_df["fasting_glucose"] * bio_df["fasting_insulin"]) / 405

    numerical_cols = ["Age", "fasting_glucose", "fasting_insulin", "BMI", "HOMA_IR", "HbA1c"]
    scaler = MinMaxScaler()
    bio_df[numerical_cols] = scaler.fit_transform(bio_df[numerical_cols])

    # Manually encode the meal_category into integer values
    meal_map = {"breakfast": 0, "lunch": 1, "dinner": 2}
    encoded_meal = meal_map.get(meal_category.lower(), 3)  # default to 3 for unknown

    feature_row = {
        "protein": protein,
        "fat": fat,
        "carbs": carbs,
        "meal_category": encoded_meal,
        "microbe_gut_health_binary": 1 if gut_health.lower() == "good" else 0
    }

    base_input = pd.DataFrame([{**feature_row, **bio_df.iloc[0].to_dict(), **micro_df.iloc[0].to_dict()}])

    # === Run predictions for both targets ===
    results = {}
    for target in ["glucose_spike_30min", "glucose_spike_60min"]:
        model_obj = models[target]
        model = model_obj["pipeline"]
        expected_features = model_obj["features"]

        for col in expected_features:
            if col not in base_input.columns:
                base_input[col] = 0

        input_aligned = base_input[expected_features]
        prediction = model.predict(input_aligned)[0]
        results[target] = round(float(prediction), 2)

    # === Glucose response interpretation ===
    threshold = 30
    if results["glucose_spike_30min"] > threshold or results["glucose_spike_60min"] > threshold:
        message = "This food is likely to increase your glucose levels."
    else:
        message = "This food appears to be safe for your glucose response."

    return {
        "glucose_spike_30min": results["glucose_spike_30min"],
        "glucose_spike_60min": results["glucose_spike_60min"],
        "message": message
    }