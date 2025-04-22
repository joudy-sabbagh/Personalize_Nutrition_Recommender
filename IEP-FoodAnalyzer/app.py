# RUN: uvicorn app:app --reload --port 8001

import os
import base64
from tempfile import NamedTemporaryFile
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Load Environment Variables 
load_dotenv()  
CLARIFAI_PAT      = os.getenv("CLARIFAI_PAT")
CLARIFAI_USER_ID  = os.getenv("CLARIFAI_USER_ID")
CLARIFAI_APP_ID   = os.getenv("CLARIFAI_APP_ID")

if not CLARIFAI_PAT or not CLARIFAI_USER_ID or not CLARIFAI_APP_ID:
    raise RuntimeError(
        "Missing Clarifai credentials in .env. "
        "Ensure CLARIFAI_PAT, CLARIFAI_USER_ID, and CLARIFAI_APP_ID are set."
    )

# Clarifai Model Configuration 
MODEL_ID         = "food-item-recognition"
MODEL_VERSION_ID = "1d5fd481e0cf4826aa72ec3ff049e044"
API_URL = (
    f"https://api.clarifai.com/v2/models/{MODEL_ID}"
    f"/versions/{MODEL_VERSION_ID}/outputs"
)

# FastAPI App Setup 
app = FastAPI(title="IEP-FoodAnalyzer")

# Allow all CORS for testing; tighten in production if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/generate-labels")
async def generate_labels(image: UploadFile = File(...)):
    """
    Accepts a multipart/form-data upload under 'image',
    forwards it to Clarifai, and returns detected food concepts.
    """
    # 1) Validate upload
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")
    # 2) Save to a temp file
    with NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(await image.read())
        tmp_path = tmp.name
    try:
        # 3) Read & base64-encode
        with open(tmp_path, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode()
        # 4) Build Clarifai REST payload
        payload = {
            "user_app_id": {
                "user_id": CLARIFAI_USER_ID,
                "app_id":  CLARIFAI_APP_ID
            },
            "inputs": [
                { "data": { "image": { "base64": b64_data } } }
            ]
        }
        headers = {
            "Authorization": f"Key {CLARIFAI_PAT}",
            "Content-Type":  "application/json"
        }
        # 5) Call Clarifai
        resp = requests.post(API_URL, headers=headers, json=payload)
        resp.raise_for_status()
        # 6) Parse out concepts (name + confidence)
        outputs  = resp.json().get("outputs", [])
        if not outputs:
            return JSONResponse(status_code=502, content={"error": "No output from Clarifai"})
        concepts = outputs[0]["data"].get("concepts", [])
        labels = [
            {"name": c["name"], "confidence": round(c["value"] * 100, 2)}
            for c in concepts
        ]
        return {"labels": labels}
    except requests.HTTPError as http_err:
        # Pass through Clarifai’s error message
        return JSONResponse(status_code=http_err.response.status_code, content=http_err.response.json())
    finally:
        # 7) Clean up temp file
        try:
            os.remove(tmp_path)
        except OSError:
            pass
