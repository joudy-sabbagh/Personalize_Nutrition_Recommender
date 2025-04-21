# RUN: uvicorn app:app --host 0.0.0.0 --port 8000

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import requests
import io

app = FastAPI()

@app.post("/analyze-meal")
def analyze_meal(image: UploadFile = File(...)):
    image_bytes = image.file.read()
    
    caption_response = requests.post(
        "http://localhost:8001/generate-caption",
        files={"image": ("filename.jpg", image_bytes, image.content_type)}
    )
    if caption_response.status_code != 200:
        return {"error": "Caption failed", "details": caption_response.text}
    caption = caption_response.json()["caption"]

    nutrition_response = requests.post(
        "http://localhost:8002/predict-nutrition",
        json={"caption": caption}
    )
    if nutrition_response.status_code != 200:
        return {"error": "Nutrition failed", "details": nutrition_response.text}
    nutrition = nutrition_response.json()

    return {
        "caption": caption,
        "nutrition": nutrition
    }

@app.post("/predict-gut-health")
def predict_gut_health(file: UploadFile = File(...)):
    csv_bytes = file.file.read()

    gut_response = requests.post(
        "http://localhost:8003/predict-gut-health-file",
        files={"file": ("subject.csv", csv_bytes, file.content_type)}
    )
    if gut_response.status_code != 200:
        return {"error": "Gut health prediction failed", "details": gut_response.text}
    return gut_response.json()


@app.post("/predict-glucose-from-all")
def predict_glucose_from_all(
    image: UploadFile = File(...),
    bio_file: UploadFile = File(...),
    micro_file: UploadFile = File(...),
    meal_category: str = Form(...)
):
    try:
        # === Step 0: Macro mapping for string → int ===
        macro_map = {"low": 1, "medium": 2, "high": 3}

        # === Read image and rewrap files ===
        image_bytes = image.file.read()
        micro_bytes = micro_file.file.read()
        bio_bytes = bio_file.file.read()

        # === STEP 1: Analyze meal ===
        analyze_response = requests.post(
            "http://localhost:8000/analyze-meal",
            files={"image": ("meal.jpg", image_bytes, image.content_type)}
        )
        if analyze_response.status_code != 200:
            return {"error": "analyze-meal failed", "details": analyze_response.text}
        analyze = analyze_response.json()
        caption = analyze["caption"]
        
        # Nutrition might be nested inside another "nutrition"
        nutrition = analyze["nutrition"]
        if "nutrition" in nutrition:
            nutrition = nutrition["nutrition"]

        # === STEP 2: Predict gut health ===
        gut_response = requests.post(
            "http://localhost:8000/predict-gut-health",
            files={"file": ("micro.csv", micro_bytes, micro_file.content_type)}
        )
        if gut_response.status_code != 200:
            return {"error": "predict-gut-health failed", "details": gut_response.text}
        gut_health = gut_response.json().get("gut_health", "bad")

        # === STEP 3: Call glucose predictor ===
        glucose_response = requests.post(
            "http://localhost:8004/predict-glucose",
            data={
                "protein": macro_map.get(nutrition["protein"], 0),
                "fat": macro_map.get(nutrition["fat"], 0),
                "carbs": macro_map.get(nutrition["carbs"], 0),
                "gut_health": gut_health,
                "meal_category": meal_category
            },
            files={
                "bio_file": ("bio.csv", bio_bytes, bio_file.content_type),
                "micro_file": ("micro.csv", micro_bytes, micro_file.content_type)
            }
        )
        if glucose_response.status_code != 200:
            return {"error": "glucose prediction failed", "details": glucose_response.text}
        glucose = glucose_response.json()

        return {
            "caption": caption,
            "nutrition": nutrition,
            "gut_health": gut_health,
            "glucose_prediction": glucose
        }

    except Exception as e:
        return {"error": f"Internal server error: {str(e)}"}