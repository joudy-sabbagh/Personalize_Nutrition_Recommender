# RUN: uvicorn app:app --host 0.0.0.0 --port 8000

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import requests

app = FastAPI()

@app.post("/analyze-meal")
async def analyze_meal(
    image: UploadFile = File(...),
    description: str = Form(None)
):
    image_bytes = await image.read()
    # === Step 1: Clarifai label extraction ===
    caption_response = requests.post(
        "http://localhost:8001/generate-labels",
        files={"image": ("filename.jpg", image_bytes, image.content_type)}
    )
    if caption_response.status_code != 200:
        return {"error": "Caption failed", "details": caption_response.text}
    labels = [
        label for label in caption_response.json().get("labels", [])
        if label.get("confidence", 0) >= 75
    ]
    if not labels and (not description or description.strip().lower() == "none"):
        return {
            "error": "Image not clear",
            "message": "No ingredients were confidently detected from the image. Please provide a description of the meal to improve prediction."
        }
    ingredient_caption = "A dish containing " + ", ".join([
    f"{label['name']} ({round(label['confidence'], 1)}%)"
        for label in labels
    ]) if labels else ""
    if description and description.strip().lower() != "none":
        if ingredient_caption:
            full_caption = f"{ingredient_caption}. Additional description: {description.strip()}"
        else:
            full_caption = description.strip()
    else:
        full_caption = ingredient_caption
    caption = full_caption
    # === Step 4: Send to nutrition predictor ===
    nutrition_response = requests.post(
        "http://localhost:8002/predict-nutrition",
        json={"caption": caption}
    )
    if nutrition_response.status_code != 200:
        return {"error": "Nutrition failed", "details": nutrition_response.text}
    nutrition = nutrition_response.json()
    return {
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
        # === Macro mapping for text → numeric encoding ===
        macro_map = {
            "extremely low": 0,
            "low": 1,
            "medium": 2,
            "high": 3,
            "extremely high": 4
        }

        # === Read input files ===
        image_bytes = image.file.read()
        micro_bytes = micro_file.file.read()
        bio_bytes = bio_file.file.read()

        # === STEP 1: Analyze Meal ===
        analyze_response = requests.post(
            "http://localhost:8000/analyze-meal",
            files={"image": ("meal.jpg", image_bytes, image.content_type)}
        )
        if analyze_response.status_code != 200:
            return {"error": "analyze-meal failed", "details": analyze_response.text}

        analyze = analyze_response.json()
        caption = analyze.get("caption", "")
        nutrition = analyze.get("nutrition", {})

        if "nutrition" in nutrition:
            nutrition = nutrition["nutrition"]

        # === STEP 2: Predict Gut Health ===
        gut_response = requests.post(
            "http://localhost:8000/predict-gut-health",
            files={"file": ("micro.csv", micro_bytes, micro_file.content_type)}
        )
        if gut_response.status_code != 200:
            return {"error": "predict-gut-health failed", "details": gut_response.text}
        gut_health = gut_response.json().get("gut_health", "bad")

        # === STEP 3: Predict Glucose Spike ===
        glucose_response = requests.post(
            "http://localhost:8004/predict-glucose",
            data={
                "protein": nutrition.get("protein_pct", 0),
                "fat": nutrition.get("fat_pct", 0),
                "carbs": nutrition.get("carbs_pct", 0),
                "sugar_risk": nutrition.get("sugar_risk", 0),
                "refined_carb": nutrition.get("refined_carb", 0),
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
