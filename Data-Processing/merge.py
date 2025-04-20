import pandas as pd
from pathlib import Path

root = Path("Data-Processing")   
microbes_fp = root /"Dataset"/ "microbes.csv"
targets_fp  = root / "gut_health_target.csv"


df_microbes = pd.read_csv(microbes_fp)

df_targets  = (
    pd.read_csv(targets_fp, usecols=["subject", "gut_health_category"])
    .drop_duplicates("subject")                          # in case of repeats
)

df_out = df_microbes.merge(df_targets, on="subject", how="left")


out_fp = root / "microbes_and_gut_health.csv"
df_out.to_csv(out_fp, index=False)

print(f"✅  File written: {out_fp.absolute()}")
