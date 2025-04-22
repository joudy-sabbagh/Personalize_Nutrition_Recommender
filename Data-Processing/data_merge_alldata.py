import os
import pandas as pd
from glob import glob

# === Configuration ===
data_dir = "Dataset"
glucose_dir = os.path.join(data_dir, "GlucoseSpike_Data")
clinical_path = os.path.join(data_dir, "filtered_clinical_data.csv")
microbiome_path = os.path.join(data_dir, "filtered_microbes_and_gut.csv")
glucose_files = sorted(glob(os.path.join(glucose_dir, "Glucose_Spike_User*.csv")))

# === Load shared subject-level data ===
clinical_df = pd.read_csv(clinical_path)
microbiome_df = pd.read_csv(microbiome_path)

# === Output list for merged rows ===
combined_rows = []

# === Process each user's glucose file ===
for file_path in glucose_files:
    print(file_path)
    filename = os.path.basename(file_path)
    subject_id = int(filename.split("User")[-1].split(".")[0])

    meal_df = pd.read_csv(file_path)

    if 'subject' not in meal_df.columns:
        meal_df['subject'] = subject_id

    clinical_row = clinical_df[clinical_df['subject'] == subject_id]
    microbiome_row = microbiome_df[microbiome_df['subject'] == subject_id]

    if clinical_row.empty or microbiome_row.empty:
        print(f"Skipping subject {subject_id} (missing clinical or microbiome data)")
        continue

    clinical_flat = clinical_row.iloc[0].add_prefix("clinical_")
    microbiome_flat = microbiome_row.iloc[0].add_prefix("microbe_")

    for _, meal in meal_df.iterrows():
        combined_row = pd.concat([meal, clinical_flat, microbiome_flat])
        combined_rows.append(combined_row)

# === Create final DataFrame ===
combined_df = pd.DataFrame(combined_rows)

# === Drop duplicate columns ===
combined_df = combined_df.loc[:, ~combined_df.columns.duplicated()]

# === Remove unwanted subjects ===
excluded_subjects = [46, 47, 49]
combined_df = combined_df[~combined_df['subject'].isin(excluded_subjects)]

# === Drop specific unwanted columns if they exist ===
cols_to_drop = ["food_img", "clinical_subject", "microbe_subject"]
combined_df.drop(columns=[col for col in cols_to_drop if col in combined_df.columns], inplace=True)

# === Convert timestamp to meal category and then drop it ===
def categorize_meal_time(timestamp):
    try:
        hour = pd.to_datetime(timestamp).hour
        if 4 <= hour < 11:
            return "breakfast"
        elif 11 <= hour < 17:
            return "lunch"
        else:
            return "dinner"
    except:
        return "unknown"

if "timestamp" in combined_df.columns:
    combined_df["meal_category"] = combined_df["timestamp"].apply(categorize_meal_time)
    combined_df.drop(columns=["timestamp"], inplace=True)

# === Drop rows with missing values ===
combined_df.dropna(inplace=True)

# === Keep only the row with highest glucose spike per subject+meal ===
if {"meal_id", "glucose_spike_30min", "subject"}.issubset(combined_df.columns):
    combined_df = combined_df.loc[
        combined_df.groupby(["subject", "meal_id"])["glucose_spike_30min"].idxmax()
    ].reset_index(drop=True)

    # Drop subject and meal_id after grouping
    combined_df.drop(columns=["subject", "meal_id"], inplace=True)

# === Save merged dataset ===
output_path = os.path.join(data_dir, "filtered_merged_alldata.csv")
combined_df.to_csv(output_path, index=False)

print(f"\nCleaned merged dataset saved to {output_path} with {len(combined_df)} rows and {len(combined_df.columns)} columns.")