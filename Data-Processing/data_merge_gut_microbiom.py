import os
import pandas as pd

# === Define base path ===
root = os.path.join("Dataset")
microbes_fp = os.path.join(root, "original_microbes.csv")
targets_fp  = os.path.join(root, "cleaned_gut_health.csv")

# === Read CSV files ===
df_microbes = pd.read_csv(microbes_fp)

df_targets = (
    pd.read_csv(targets_fp, usecols=["subject", "gut_health_category"])
    .drop_duplicates(subset="subject")
)

# === Merge on subject ===
df_out = pd.merge(df_microbes, df_targets, on="subject", how="left")

# === Remove rows with missing gut_health_category ===
df_out = df_out.dropna(subset=["gut_health_category"])

# === Output path and save ===
out_fp = os.path.join(root, "cleaned_microbes_and_gut.csv")
df_out.to_csv(out_fp, index=False)

print(f"File written (nulls removed): {os.path.abspath(out_fp)}")
