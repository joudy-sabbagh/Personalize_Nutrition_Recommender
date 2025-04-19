from fastapi import FastAPI, File, UploadFile
import requests

app = FastAPI()

@app.post("/analyze-meal")
def analyze_meal(image: UploadFile = File(...)):
    # Step 1: Read image
    image_bytes = image.file.read()

    # Step 2: Get caption
    caption_response = requests.post(
        "http://localhost:8001/generate-caption",
        files={"image": ("filename.jpg", image_bytes, image.content_type)}
    )
    if caption_response.status_code != 200:
        return {"error": "Caption failed", "details": caption_response.text}

    caption = caption_response.json()["caption"]

    # Step 3: Get nutrition from caption
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
