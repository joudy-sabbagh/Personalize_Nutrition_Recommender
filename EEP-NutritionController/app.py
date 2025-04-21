# RUN: uvicorn app:app --host 0.0.0.0 --port 8000
 
from fastapi import FastAPI, File, UploadFile
import requests

app = FastAPI()

@app.post("/analyze-meal")
def analyze_meal(image: UploadFile = File(...)):
    # read the image
    image_bytes = image.file.read()
    # send request to IEP-FoodAnalyzer to get a caption description of the meal
    caption_response = requests.post(
        "http://localhost:8001/generate-caption",
        files={"image": ("filename.jpg", image_bytes, image.content_type)}
    )
    if caption_response.status_code != 200:
        return {"error": "Caption failed", "details": caption_response.text}
    # save the caption
    caption = caption_response.json()["caption"]
    # send request to IEP-NutritionPredictor to get a nutrition estimate of the image given the caption
    nutrition_response = requests.post(
        "http://localhost:8002/predict-nutrition",
        json={"caption": caption}
    )
    if nutrition_response.status_code != 200:
        return {"error": "Nutrition failed", "details": nutrition_response.text}
    nutrition = nutrition_response.json()
    # for now, return both caption and nutrition
    return {
        "caption": caption,
        "nutrition": nutrition
    }

@app.post("/predict-gut-health")
def predict_gut_health(file: UploadFile = File(...)):
    # Read the uploaded CSV
    csv_bytes = file.file.read()
    # Call Gut Health Predictor (port 8003)
    gut_response = requests.post(
        "http://localhost:8003/predict-gut-health-file",
        files={"file": ("subject.csv", csv_bytes, file.content_type)}
    )
    if gut_response.status_code != 200:
        return {"error": "Gut health prediction failed", "details": gut_response.text}
    return gut_response.json()