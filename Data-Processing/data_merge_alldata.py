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
        print(f"⚠️ Skipping subject {subject_id} (missing clinical or microbiome data)")
        continue

    clinical_flat = clinical_row.iloc[0].add_prefix("clinical_")
    microbiome_flat = microbiome_row.iloc[0].add_prefix("microbe_")

    for _, meal in meal_df.iterrows():
        combined_row = pd.concat([meal, clinical_flat, microbiome_flat])
        combined_rows.append(combined_row)

# === Create final DataFrame ===
combined_df = pd.DataFrame(combined_rows)

# === Drop duplicate columns and empty rows ===
combined_df = combined_df.loc[:, ~combined_df.columns.duplicated()]
combined_df.dropna(inplace=True)

# === Save merged dataset ===
output_path = os.path.join(data_dir, "filtered_merged_alldata.csv")
combined_df.to_csv(output_path, index=False)

print(f"\nCleaned merged dataset saved to {output_path} with {len(combined_df)} rows and {len(combined_df.columns)} columns.")
