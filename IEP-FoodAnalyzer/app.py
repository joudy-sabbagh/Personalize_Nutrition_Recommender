# RUN: uvicorn app:app --reload --port 8001

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import requests
import os
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN") 
API_URL = "https://api-inference.huggingface.co/models/nlpconnect/vit-gpt2-image-captioning"
headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

app = FastAPI()

# GENERATE CAPTION USING VIT-GPT2-IMAGE-CAPTIONING THROUGH API CALL -> RETURN CAPTION
@app.post("/generate-caption")
async def generate_caption(image: UploadFile = File(...)):
    image_bytes = await image.read()
    response = requests.post(
        API_URL,
        headers=headers,
        data=image_bytes
    )
    if response.status_code == 200:
        caption = response.json()[0]["generated_text"]
        return {"caption": caption}
    else:
        return JSONResponse(
            status_code=response.status_code,
            content={"error": "Captioning failed", "details": response.text}
        )
