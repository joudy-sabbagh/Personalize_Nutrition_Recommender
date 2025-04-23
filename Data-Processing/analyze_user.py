import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error

# === Load data ===
df = pd.read_csv("Dataset/combined_features_glucose.csv")

# Check for subject column
if "subject" not in df.columns:
    raise ValueError("Dataset must contain a 'subject' column for patient ID.")

# Remove rows with missing glucose values
df = df.dropna(subset=["glucose_spike_30min", "glucose_spike_60min"])

# === Results container ===
user_results = []

# === Loop over each subject ===
for subject_id, group in df.groupby("subject"):
    if len(group) < 5:
        continue  # Skip if too few meals

    # === Extract features and targets ===
    X = group.drop(columns=["glucose_spike_30min", "glucose_spike_60min", "subject"])
    y_30 = group["glucose_spike_30min"]
    y_60 = group["glucose_spike_60min"]

    # === One-hot encode categorical features ===
    X = pd.get_dummies(X, columns=["clinical_Gender", "meal_category"], drop_first=True)

    # === Split train/test for each target ===
    X_train, X_test, y_train_30, y_test_30 = train_test_split(X, y_30, test_size=0.25, random_state=42)
    _, _, y_train_60, y_test_60 = train_test_split(X, y_60, test_size=0.25, random_state=42)

    # === Train and evaluate for glucose_spike_30min ===
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train_30)
    preds_30 = model.predict(X_test)
    r2_30 = r2_score(y_test_30, preds_30)
    rmse_30 = np.sqrt(mean_squared_error(y_test_30, preds_30))

    # === Train and evaluate for glucose_spike_60min ===
    model.fit(X_train, y_train_60)
    preds_60 = model.predict(X_test)
    r2_60 = r2_score(y_test_60, preds_60)
    rmse_60 = np.sqrt(mean_squared_error(y_test_60, preds_60))

    user_results.append({
        "subject": subject_id,
        "n_meals": len(group),
        "r2_30min": r2_30,
        "rmse_30min": rmse_30,
        "r2_60min": r2_60,
        "rmse_60min": rmse_60
    })

# === Save results ===
results_df = pd.DataFrame(user_results)
results_df.to_csv("user_model_results.csv", index=False)
print("[✓] Saved per-user results to user_model_results.csv")

# === Preview top subjects by R² score ===
print("\nTop subjects (sorted by 30min R²):")
print(results_df.sort_values(by="r2_30min", ascending=False).head(10))
