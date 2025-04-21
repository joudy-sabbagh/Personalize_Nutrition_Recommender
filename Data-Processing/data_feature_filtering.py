import pandas as pd
import numpy as np
from sklearn.feature_selection import mutual_info_regression

# === Load dataset ===
df = pd.read_csv("Dataset/filtered_merged_alldata.csv")

# === Setup: features and targets ===
X = df.drop(columns=["glucose_spike_30min", "glucose_spike_60min"])
y_30 = df["glucose_spike_30min"]
y_60 = df["glucose_spike_60min"]

# === Convert object columns to category codes for MI ===
for col in X.select_dtypes(include="object").columns:
    X[col] = X[col].astype("category").cat.codes

# === Calculate Pearson + Mutual Information ===
correlation_30 = X.apply(lambda col: np.corrcoef(col, y_30)[0, 1] if col.std() > 0 else 0)
correlation_60 = X.apply(lambda col: np.corrcoef(col, y_60)[0, 1] if col.std() > 0 else 0)
mi_30 = mutual_info_regression(X, y_30)
mi_60 = mutual_info_regression(X, y_60)

# === Combine into a feature importance dataframe ===
feature_scores = pd.DataFrame({
    "Feature": X.columns,
    "Pearson_30min": correlation_30,
    "Pearson_60min": correlation_60,
    "MI_30min": mi_30,
    "MI_60min": mi_60
})

# === Step 1: Keep features with strong MI or Pearson ===
selected_features = feature_scores[
    (feature_scores["MI_30min"] > 0.02) | (feature_scores["MI_60min"] > 0.02) |
    (feature_scores["Pearson_30min"].abs() > 0.05) | (feature_scores["Pearson_60min"].abs() > 0.05)
]["Feature"].tolist()

X_filtered = X[selected_features].copy()

# === Step 2: Add interaction features ===
if "clinical_fasting_glucose" in X_filtered.columns and "carbs" in X_filtered.columns:
    X_filtered["carbs_x_glucose"] = X_filtered["carbs"] * X_filtered["clinical_fasting_glucose"]

if "clinical_HOMA_IR" in X_filtered.columns and "protein" in X_filtered.columns:
    X_filtered["protein_x_HOMA_IR"] = X_filtered["protein"] * X_filtered["clinical_HOMA_IR"]

if "fat" in X_filtered.columns and "microbe_gut_health_binary" in X_filtered.columns:
    X_filtered["fat_x_gut_health"] = X_filtered["fat"] * X_filtered["microbe_gut_health_binary"]

# === Add targets back before saving ===
X_filtered["glucose_spike_30min"] = y_30
X_filtered["glucose_spike_60min"] = y_60

# === Save filtered dataset ===
X_filtered.to_csv("Dataset/filtered_final_features.csv", index=False)

# === Print summary ===
print(f"Started with {X.shape[1]} features")
print(f"Kept {X_filtered.shape[1] - 2} features (excluding targets)")
print("Saved filtered dataset to Dataset/filtered_final_features.csv")
