import pandas as pd
import os

# === File paths ===
root = "Dataset"
clinical_fp = os.path.join(root, "cleaned_clinical_data.csv")
microbes_fp = os.path.join(root, "cleaned_microbes_and_gut.csv")

# === Load the CSV files ===
df_clinical = pd.read_csv(clinical_fp)
df_microbes = pd.read_csv(microbes_fp)

# === Get common subjects ===
common_subjects = set(df_clinical["subject"]).intersection(df_microbes["subject"])

# === Remove specified users
users_to_remove = {24, 25, 37, 40}
final_subjects = common_subjects - users_to_remove

# === Filter both DataFrames ===
df_clinical_filtered = df_clinical[df_clinical["subject"].isin(final_subjects)].copy()
df_microbes_filtered = df_microbes[df_microbes["subject"].isin(final_subjects)].copy()

# === Save filtered files ===
clinical_out_fp = os.path.join(root, "filtered_clinical_data.csv")
microbes_out_fp = os.path.join(root, "filtered_microbes_and_gut.csv")

df_clinical_filtered.to_csv(clinical_out_fp, index=False)
df_microbes_filtered.to_csv(microbes_out_fp, index=False)

print(f"Final subjects kept: {len(final_subjects)}")
print(f"Saved to:\n- {clinical_out_fp}\n- {microbes_out_fp}")
