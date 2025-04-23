import pandas as pd

# === Paths ===
data_path = "Dataset/filtered_merged_alldata.csv"
top_bacteria_path = "Dataset/top_bacteria_union.csv"

# === Load full data and top bacteria ===
df = pd.read_csv(data_path)
top_bacteria = pd.read_csv(top_bacteria_path)["bacteria"].tolist()

# === Define additional features ===
macro_feats = ["protein_pct", "carbs_pct", "fat_pct", "sugar_risk", "refined_carb"]
clinical_feats = [
    "subject","clinical_Age", "clinical_BMI", "clinical_fasting_glucose",
    "clinical_fasting_insulin", "clinical_HbA1c", "clinical_HOMA_IR"
]
categorical_feats = ["clinical_Gender", "meal_category"]
targets = ["glucose_spike_30min", "glucose_spike_60min"]

# === Subset the dataframe ===
selected_cols = top_bacteria + macro_feats + clinical_feats + categorical_feats + targets
df_selected = df[selected_cols]

# === Save new dataset ===
df_selected.to_csv("Dataset/combined_features_glucose.csv", index=False)
print("Saved combined feature dataset to Dataset/combined_features_glucose.csv")