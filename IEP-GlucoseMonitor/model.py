import os
import math
import joblib
import shap
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.feature_selection import VarianceThreshold, SelectKBest, f_regression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score, cross_val_predict, KFold
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# === Config ===
PROJECT_ROOT = Path(__file__).parent.parent
CSV_FILE = PROJECT_ROOT / "Data-Processing" / "Dataset" / "filtered_final_features.csv"
MODEL_DIR = Path(__file__).parent
MODEL_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42
KFOLDS = 3
TOP_K = 100

def load_data(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df.dropna(inplace=True)
    return df

def build_pipeline(k_best=TOP_K):
    model = HistGradientBoostingRegressor(random_state=RANDOM_STATE)
    pipeline = Pipeline([
        ("var", VarianceThreshold(threshold=0.005)),
        ("select", SelectKBest(f_regression, k=k_best)),
        ("scale", StandardScaler(with_mean=False)),
        ("model", model)
    ])
    return pipeline

def evaluate_model(pipe, X, y, name):
    cv = KFold(n_splits=KFOLDS, shuffle=True, random_state=RANDOM_STATE)
    preds = cross_val_predict(pipe, X, y, cv=cv, n_jobs=-1)
    r2 = r2_score(y, preds)
    mae = mean_absolute_error(y, preds)
    rmse = math.sqrt(mean_squared_error(y, preds))
    std = cross_val_score(pipe, X, y, cv=cv, scoring="r2", n_jobs=-1).std()
    print(f"{name} | CV R2={r2:.3f} (±{std:.3f}) | MAE={mae:.2f} | RMSE={rmse:.2f}")
    return dict(R2=r2, MAE=mae, RMSE=rmse)

def train_and_save(df: pd.DataFrame, target: str):
    print(f"\n--- Training for {target} ---")
    X = df.drop(columns=["glucose_spike_30min", "glucose_spike_60min"])
    y = df[target].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE)
    pipeline = build_pipeline()
    print("Fitting pipeline...")
    pipeline.fit(X_train, y_train)
    evaluate_model(pipeline, X_test, y_test, name=target)

    out = MODEL_DIR / f"{target}_model.joblib"
    joblib.dump({
        "pipeline": pipeline,
        "features": X.columns.tolist(),
        "meta": {
            "created": pd.Timestamp.now().isoformat(),
            "model_type": "TreeOnly",
            "top_k": TOP_K,
            "kfolds": KFOLDS
        }
    }, out)
    print(f"Saved model → {out.name}")

    # === SHAP analysis ===
    print(f"Running SHAP analysis for {target}...")
    try:
        # Fit pipeline and extract model + feature names
        pipeline.fit(X_train, y_train)
        model = pipeline.named_steps["model"]
        selector = pipeline.named_steps["select"]
        selected_indices = selector.get_support(indices=True)
        selected_features = X.columns[selected_indices]

        X_train_selected = pipeline.named_steps["scale"].fit_transform(
            selector.transform(pipeline.named_steps["var"].transform(X_train))
        )

        explainer = shap.Explainer(model.predict, X_train_selected)
        shap_values = explainer(X_train_selected[:100])  # Limit to 100 samples for speed

        shap.summary_plot(shap_values, features=X_train_selected[:100], feature_names=selected_features, show=True)
    except Exception as e:
        print(f"SHAP analysis failed: {e}")

# === Main ===
if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    print(f"Loading from: {CSV_FILE}")
    df = load_data(CSV_FILE)
    train_and_save(df, "glucose_spike_30min")
    train_and_save(df, "glucose_spike_60min")
