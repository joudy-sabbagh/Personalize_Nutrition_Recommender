import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import ElasticNet
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor, VotingRegressor
from sklearn.metrics import r2_score, mean_squared_error

mlflow.set_tracking_uri("http://localhost:5000")

# === Load Data ===
results = pd.read_csv("../Data-Processing/Dataset/user_model_results.csv")
top_subjects = results.sort_values(by="r2_30min", ascending=False).head(10)["subject"].tolist()
df = pd.read_csv("../Data-Processing/Dataset/combined_features_glucose.csv")
df = df[df["subject"].isin(top_subjects)]

X = df.drop(columns=["glucose_spike_30min", "glucose_spike_60min", "subject"])
y = df["glucose_spike_60min"]

categorical_cols = ["clinical_Gender", "meal_category"]
preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
        ("scale", StandardScaler(), X.select_dtypes(include="number").columns.tolist())
    ],
    remainder="passthrough"
)

# === Model Versions ===
model_versions = {
    "v1": {
        "enet": ElasticNet(alpha=0.1, l1_ratio=0.5),
        "rf": RandomForestRegressor(n_estimators=100, random_state=42),
        "hgb": HistGradientBoostingRegressor(random_state=42),
    },
    "v2": {
        "enet": ElasticNet(alpha=0.05, l1_ratio=0.8),
        "rf": RandomForestRegressor(n_estimators=300, max_depth=10, min_samples_leaf=3, random_state=42),
        "hgb": HistGradientBoostingRegressor(max_iter=300, learning_rate=0.03, max_depth=7, random_state=42),
    },
    "v3": {
        "enet": ElasticNet(alpha=0.03, l1_ratio=0.85),
        "rf": RandomForestRegressor(n_estimators=300, max_depth=12, min_samples_leaf=4, random_state=42),
        "hgb": HistGradientBoostingRegressor(learning_rate=0.02, max_iter=500, max_depth=6, min_samples_leaf=5, random_state=42),
    }
}

# === Train + Log Each Version ===
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

for version, models in model_versions.items():
    enet, rf, hgb = models["enet"], models["rf"], models["hgb"]
    ensemble = VotingRegressor(estimators=[("enet", enet), ("rf", rf), ("hgb", hgb)])

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", ensemble)
    ])

    with mlflow.start_run(run_name=f"VotingRegressor_{version}"):
        pipeline.fit(X_train, y_train)
        preds = pipeline.predict(X_test)

        r2 = r2_score(y_test, preds)
        rmse = np.sqrt(mean_squared_error(y_test, preds))

        # Log parameters
        mlflow.log_param("version", version)
        mlflow.log_param("enet_alpha", enet.alpha)
        mlflow.log_param("enet_l1_ratio", enet.l1_ratio)
        mlflow.log_param("rf_estimators", rf.n_estimators)
        mlflow.log_param("rf_max_depth", rf.max_depth)
        mlflow.log_param("rf_min_samples_leaf", getattr(rf, "min_samples_leaf", None))
        mlflow.log_param("hgb_lr", getattr(hgb, "learning_rate", None))
        mlflow.log_param("hgb_max_iter", getattr(hgb, "max_iter", None))
        mlflow.log_param("hgb_max_depth", getattr(hgb, "max_depth", None))

        # Log metrics
        mlflow.log_metric("r2", r2)
        mlflow.log_metric("rmse", rmse)

        # Save model
        mlflow.sklearn.log_model(pipeline, artifact_path=f"model_{version}")
        print(f"[✓] Version {version} logged | R² = {r2:.3f}, RMSE = {rmse:.3f}")
