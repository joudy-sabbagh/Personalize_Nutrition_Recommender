from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv
import re
from typing import List, Optional

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

class RecommendationRequest(BaseModel):
    user_id: str
    meal_type: str  # breakfast, lunch, dinner, snack
    nutrition_goal: str  # bulking, cutting, maintaining
    caption: str  # description of the meal from image analysis

class Recommendation(BaseModel):
    original_ingredient: str
    suggested_replacement: str
    reason: str

class RecommendationResponse(BaseModel):
    meal_overview: str
    nutritional_assessment: str
    recommendations: List[Recommendation]
    general_advice: str

@app.post("/recommend-meal", response_model=RecommendationResponse)
async def recommend_meal(request: RecommendationRequest):
    """
    Generate personalized meal recommendations based on:
    - User's fitness goal (bulking, cutting, maintaining)
    - Meal type (breakfast, lunch, dinner, snack)
    - Meal caption (description of current meal)
    """
    # Validate request parameters
    if request.nutrition_goal.lower() not in ["bulking", "cutting", "maintaining"]:
        raise HTTPException(status_code=400, detail="Nutrition goal must be 'bulking', 'cutting', or 'maintaining'")
    
    if request.meal_type.lower() not in ["breakfast", "lunch", "dinner", "snack"]:
        raise HTTPException(status_code=400, detail="Meal type must be 'breakfast', 'lunch', 'dinner', or 'snack'")
    
    # Prepare prompt for OpenAI
    prompt = f"""
    As a nutritionist and dietitian, analyze this meal and provide recommendations based on the user's fitness goal.
    
    MEAL TYPE: {request.meal_type}
    FITNESS GOAL: {request.nutrition_goal}
    MEAL DESCRIPTION: {request.caption}
    
    Provide a detailed response with the following sections:
    
    1. MEAL OVERVIEW: A brief description of the meal as described.
    
    2. NUTRITIONAL ASSESSMENT: Analyze the nutritional value of this meal in relation to the user's fitness goal.
    
    3. INGREDIENT RECOMMENDATIONS: Suggest 3-5 specific ingredient replacements or additions that would better align with the user's fitness goal.
    For each recommendation, provide:
    - Original ingredient to replace (or area to improve)
    - Suggested replacement or addition
    - Specific reason for this recommendation related to their fitness goal
    
    4. GENERAL ADVICE: Provide 2-3 sentences of general advice about this meal type for the specific fitness goal.
    
    Format the ingredient recommendations as: 
    [Original: original_ingredient | Replacement: suggested_replacement | Reason: specific_reason]
    
    Be specific and practical with recommendations. If bulking, focus on nutrient-dense caloric additions. If cutting, focus on lower-calorie substitutes that maintain satiety. If maintaining, focus on balanced macronutrients.
    """
    
    try:
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert nutritionist specializing in fitness nutrition."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extract the content from the response
        content = response['choices'][0]['message']['content'].strip()
        
        # Parse the response
        sections = content.split("\n\n")
        meal_overview = ""
        nutritional_assessment = ""
        recommendations_text = ""
        general_advice = ""
        
        for section in sections:
            if section.startswith("1. MEAL OVERVIEW:") or section.startswith("MEAL OVERVIEW:"):
                meal_overview = section.split(":", 1)[1].strip()
            elif section.startswith("2. NUTRITIONAL ASSESSMENT:") or section.startswith("NUTRITIONAL ASSESSMENT:"):
                nutritional_assessment = section.split(":", 1)[1].strip()
            elif section.startswith("3. INGREDIENT RECOMMENDATIONS:") or section.startswith("INGREDIENT RECOMMENDATIONS:"):
                recommendations_text = section.split(":", 1)[1].strip()
            elif section.startswith("4. GENERAL ADVICE:") or section.startswith("GENERAL ADVICE:"):
                general_advice = section.split(":", 1)[1].strip()
        
        # Parse the recommendations
        recommendations = []
        recommendation_pattern = r"\[Original: (.*?) \| Replacement: (.*?) \| Reason: (.*?)\]"
        matches = re.findall(recommendation_pattern, recommendations_text)
        
        for match in matches:
            recommendations.append(
                Recommendation(
                    original_ingredient=match[0].strip(),
                    suggested_replacement=match[1].strip(),
                    reason=match[2].strip()
                )
            )
        
        # If no recommendations were found with the pattern, try to extract them differently
        if not recommendations and recommendations_text:
            # Split by numbered list items or bullet points
            rec_items = re.split(r'\d+\.\s+|\-\s+', recommendations_text)
            rec_items = [item.strip() for item in rec_items if item.strip()]
            
            for item in rec_items:
                parts = item.split(":", 2)
                if len(parts) >= 3:
                    original = parts[0].strip()
                    replacement = parts[1].strip()
                    reason = parts[2].strip() if len(parts) > 2 else "Improves nutritional profile"
                    recommendations.append(
                        Recommendation(
                            original_ingredient=original,
                            suggested_replacement=replacement,
                            reason=reason
                        )
                    )
        
        # Create the response
        return RecommendationResponse(
            meal_overview=meal_overview,
            nutritional_assessment=nutritional_assessment,
            recommendations=recommendations,
            general_advice=general_advice
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Run with: uvicorn app:app --host 0.0.0.0 --port 8005
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)

