from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

class FoodDescription(BaseModel):
    caption: str

@app.post("/predict-nutrition")
def predict_nutrition(payload: FoodDescription):
    caption = payload.caption
    prompt = f"""
    Given the following food description, estimate the typical macronutrient content of the dish.
    You must guess whether each of the following is high, medium, or low: protein, fat, carbs, total calories.
    Do not answer with "varies" or "depends" — just guess based on what you'd expect from the dish.

    Format your response like this:
    [protein = , fat = , carbs = , total calories = ]

    Food description: {caption}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a nutrition expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
        )
        result = response['choices'][0]['message']['content'].strip()

        # Extract labels (high/medium/low) using regex
        import re
        def extract(label):
            match = re.search(rf"{label}\s*=\s*(high|medium|low)", result, re.IGNORECASE)
            return match.group(1).lower() if match else None

        return {
            "caption": caption,
            "nutrition": {
                "protein": extract("protein"),
                "fat": extract("fat"),
                "carbs": extract("carbs"),
            },
            "result": result
        }

    except Exception as e:
        return {"error": str(e)}