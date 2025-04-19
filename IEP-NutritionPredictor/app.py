from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv
import os
import openai

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

class FoodDescription(BaseModel):
    caption: str

@app.post("/predict-nutrition")
def predict_nutrition(payload: FoodDescription):
    caption = payload.caption
    prompt = f"""
    Given the following food description, estimate the macronutrients typically found in the dish.
    Provide the values in grams and total calories. Format your response simply as:
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
        return {"nutrition": result}
    except Exception as e:
        return {"error": str(e)}