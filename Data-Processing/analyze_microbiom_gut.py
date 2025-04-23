import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor

# === Load Data ===
DATA_PATH = "Dataset/filtered_microbiome_glucose.csv"
df = pd.read_csv(DATA_PATH)

# === Separate Features and Targets ===
X = df.drop(columns=["glucose_spike_30min", "glucose_spike_60min"])
y_30 = df["glucose_spike_30min"]
y_60 = df["glucose_spike_60min"]

def analyze_feature_importance(X, y, target_name):
    # Train Random Forest
    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X, y)

    # Get feature importances
    importances = model.feature_importances_
    importance_df = pd.DataFrame({
        "bacteria": X.columns,
        "importance": importances
    }).sort_values(by="importance", ascending=False)

    # Save top 30
    top30 = importance_df.head(30)
    top30.to_csv(f"top30_bacteria_{target_name}.csv", index=False)

    # Plot
    plt.figure(figsize=(10, 8))
    plt.barh(top30["bacteria"], top30["importance"])
    plt.gca().invert_yaxis()
    plt.xlabel("Feature Importance")
    plt.title(f"Top 30 Bacteria for {target_name}")
    plt.tight_layout()
    plt.savefig(f"top30_bacteria_{target_name}.png")
    plt.close()

    print(f"[✓] Saved top features for {target_name} to CSV and PNG.")

# === Analyze for both targets ===
analyze_feature_importance(X, y_30, "glucose_spike_30min")
analyze_feature_importance(X, y_60, "glucose_spike_60min")

top30_30min = pd.read_csv("Dataset/top30_bacteria_glucose_spike_30min.csv")
top30_60min = pd.read_csv("Dataset/top30_bacteria_glucose_spike_60min.csv")

# Get union of top bacteria
top_bacteria_union = pd.Series(
    list(set(top30_30min["bacteria"]) | set(top30_60min["bacteria"]))
)

# Save to use later
top_bacteria_union.to_csv("Dataset/top_bacteria_union.csv", index=False, header=["bacteria"])
