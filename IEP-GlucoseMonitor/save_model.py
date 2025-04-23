import mlflow.sklearn
import joblib

# Set tracking URI if needed (optional if you've already set it)
mlflow.set_tracking_uri("http://localhost:5000")

# Load the model from MLflow model registry
model_uri = "models:/glucose_model/1"
model = mlflow.sklearn.load_model(model_uri)

# Save locally using joblib (or pickle)
joblib.dump(model, "glucose_predictor_local.pkl")
print("Saved locally as glucose_predictor_local.pkl")