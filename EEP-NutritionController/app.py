from fastapi.middleware.cors import CORSMiddleware
# RUN: uvicorn app:app --host 0.0.0.0 --port 8000

from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
import requests
import os
import sys
from pydantic import BaseModel
import io
import pandas as pd
from typing import Optional

# Add Database directory to the path so we can import the db module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'Database')))
from Database.db import user_signup, user_signin, save_bacteria_data, save_clinical_data, save_meal_data, get_user_clinical_data, get_user_microbiome_data

# Schemas for user authentication
class UserSignup(BaseModel):
    username: str
    email: str
    password: str

class UserSignin(BaseModel):
    username: str
    password: str

import time

from prometheus_client import make_asgi_app, Counter, Summary, Gauge

# === Define Metrics ===
REQUEST_COUNT = Counter("request_count", "Total number of requests")
REQUEST_LATENCY = Summary("request_latency_seconds", "Request latency")
PREDICTION_VALUE = Gauge("last_prediction_value", "Last predicted value")

# === Setup App ===
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount /metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# === Example Monitoring on Endpoint ===
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    REQUEST_COUNT.inc()
    start_time = time.time()
    response = await call_next(request)
    REQUEST_LATENCY.observe(time.time() - start_time)
    return response

# Get service URLs
FOOD_ANALYZER_URL = os.environ.get('FOOD_ANALYZER_URL', 'http://localhost:8001')
NUTRITION_PREDICTOR_URL = os.environ.get('NUTRITION_PREDICTOR_URL', 'http://localhost:8002')
MICROBIOM_ANALYZER_URL = os.environ.get('MICROBIOM_ANALYZER_URL', 'http://localhost:8003')
GLUCOSE_MONITOR_URL = os.environ.get('GLUCOSE_MONITOR_URL', 'http://localhost:8004')

# Authentication routes
@app.post("/signup")
async def signup(user_data: UserSignup):
    """
    Register a new user
    """
    user_id, message = user_signup(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password
    )
    
    if user_id:
        return {"status": "success", "message": message, "user_id": user_id}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

@app.post("/signin")
async def signin(user_data: UserSignin):
    """
    Authenticate a user
    """
    user, message = user_signin(
        username=user_data.username,
        password=user_data.password
    )
    
    if user:
        return {"status": "success", "message": message, "user": user}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message
        )

@app.post("/analyze-meal")
async def analyze_meal(
    image: UploadFile = File(...),
    description: str = Form(None)
):
    image_bytes = await image.read()

    caption_response = requests.post(
        f"{FOOD_ANALYZER_URL}/generate-labels",
        files={"image": ("filename.jpg", image_bytes, image.content_type)}
    )
    if caption_response.status_code != 200:
        return {"error": "Caption failed", "details": caption_response.text}
    labels = [
        label for label in caption_response.json().get("labels", [])
        if label.get("confidence", 0) >= 20
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

    nutrition_response = requests.post(
        f"{NUTRITION_PREDICTOR_URL}/predict-nutrition",
        json={"caption": caption}
    )
    if nutrition_response.status_code != 200:
        return {"error": "Nutrition failed", "details": nutrition_response.text}

    nutrition = nutrition_response.json()

    # === Set Prometheus Metric ===
    if "sugar_risk" in nutrition:
        PREDICTION_VALUE.set(nutrition.get("sugar_risk", 0))

    return {
        "nutrition": nutrition
    }

@app.post("/predict-gut-health")
def predict_gut_health(file: UploadFile = File(...), user_id: int = Form(None)):
    try:
        # Read the CSV file content
        csv_bytes = file.file.read()
        
        # Extract bacteria data from CSV (if user_id is provided)
        bacteria_saved = False
        bact_id = None
        
        if user_id:
            # Parse the CSV content
            import pandas as pd
            import io
            
            # Reset file pointer to beginning to read the content
            file.file.seek(0)
            csv_content = io.StringIO(csv_bytes.decode('utf-8'))
            df = pd.read_csv(csv_content)
            
            # Extract bacteria presence data (assuming second row contains the 0s and 1s)
            if len(df) >= 1:  # At least one row of data after header
                # Get the first row (index 0) which contains the 0s and 1s values
                bacteria_values = df.iloc[0].astype(str).values
                # Remove any spaces and join into a single string
                bacteria_string = ''.join([val.strip() for val in bacteria_values])
                
                # Save to database
                from Database.db import save_bacteria_data
                bact_id, message = save_bacteria_data(user_id, bacteria_string)
                
                if bact_id:
                    bacteria_saved = True
                else:
                    print(f"Warning: Failed to save bacteria data: {message}")
            
            # Reset file pointer for sending to microbiome analyzer
            file.file.seek(0)
            csv_bytes = file.file.read()
        
        # Forward to microbiome analyzer service
        gut_response = requests.post(
            f"{MICROBIOM_ANALYZER_URL}/predict-gut-health-file",
            files={"file": ("subject.csv", csv_bytes, file.content_type)}
        )
        
        if gut_response.status_code != 200:
            return {"error": "Gut health prediction failed", "details": gut_response.text}
        
        # Get the analysis results
        result = gut_response.json()
        
        # Add bacteria save status if applicable
        if user_id and bacteria_saved:
            result["bacteria_saved"] = bacteria_saved
            result["bact_id"] = bact_id
            
        return result
        
    except Exception as e:
        return {"error": f"Error processing gut health data: {str(e)}"}

@app.post("/predict-glucose-from-all")
async def predict_glucose_from_all(
    image: UploadFile = File(...),
    bio_file: Optional[UploadFile] = File(None),
    micro_file: Optional[UploadFile] = File(None),
    meal_category: str = Form(...),
    use_saved_bio: bool = Form(False),
    use_saved_micro: bool = Form(False),
    user_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None)
):
    try:
        # Initialize variables
        bio_bytes = None
        micro_bytes = None
        
        # Read image file only once
        image_bytes = await image.read()
        
        # === Handle Bio Data ===
        if bio_file:
            bio_bytes = await bio_file.read()
       # --- Handle Bio Data ---
        elif user_id:
            clinical_data = get_user_clinical_data(user_id)
            if not clinical_data:
                return {"error": "No saved bio/clinical data found for this user"}

            # 1. Build a single-row DataFrame, including user_id
            df = pd.DataFrame(
                [{ **{"user_id": user_id}, **clinical_data }]
            )

            # 2. Rename to exact headers your glucose-monitor expects
            df.rename(columns={
                "user_id":                   "user_id",            # space, lowercase
                "clinical_age":              "clinical_Age",       # underscore + capital A
                "clinical_weight":           "clinical_Weight",
                "clinical_height":           "clinical_Height",
                "clinical_bmi":              "clinical_BMI",
                "clinical_fasting_glucose":  "clinical_fasting_glucose",
                "clinical_fasting_insulin":  "clinical_fasting_insulin",
                "clinical_hba1c":            "clinical_HbA1c",
                "clinical_homa_ir":          "clinical_HOMA_IR",
                "clinical_gender":           "clinical_Gender",
            }, inplace=True)

            # 3. Now serialize
            csv_buffer = io.BytesIO()
            df.to_csv(csv_buffer, index=False)
            bio_bytes = csv_buffer.getvalue()
        else:
            return {"error": "No bio file provided and no user_id to fetch saved data"}


        # === Handle Microbiome Data ===
        if user_id and use_saved_micro:
            _, bacteria_string = get_user_microbiome_data(user_id)
            if not bacteria_string:
                return {"error": "No saved microbiome data found for this user"}
            
            # Convert bacteria string to CSV format
            csv_content = ",".join(list(bacteria_string))
            micro_bytes = io.BytesIO(csv_content.encode('utf-8')).getvalue()
        elif micro_file:
            micro_bytes = await micro_file.read()
        else:
            return {"error": "Microbiome file is required or use_saved_micro must be true"}

        # === STEP 1: Analyze Meal ===
        # Reset image file pointer if needed (just in case)
        image.file.seek(0)
        image_bytes = await image.read()
        
        # Send to food analyzer service
        caption_response = requests.post(
            f"{FOOD_ANALYZER_URL}/generate-labels",
            files={"image": ("meal.jpg", image_bytes, image.content_type)}
        )
        
        if caption_response.status_code != 200:
            return {"error": "Caption failed", "details": caption_response.text}
        
        # Process labels
        labels = [
            label for label in caption_response.json().get("labels", [])
            if label.get("confidence", 0) >= 20
        ]
        
        # Handle case where no labels detected
        if not labels and (not description or description.strip().lower() == "none"):
            return {
                "error": "Image not clear",
                "message": "No ingredients were confidently detected from the image. Please provide a description of the meal to improve prediction."
            }
        
        # Build caption
        ingredient_caption = "A dish containing " + ", ".join([
            f"{label['name']} ({round(label['confidence'], 1)}%)"
            for label in labels
        ]) if labels else ""
        
        if description and description.strip().lower() != "none":
            full_caption = f"{ingredient_caption}. Additional description: {description.strip()}" if ingredient_caption else description.strip()
        else:
            full_caption = ingredient_caption

        # Get nutrition prediction
        nutrition_response = requests.post(
            f"{NUTRITION_PREDICTOR_URL}/predict-nutrition",
            json={"caption": full_caption}
        )
        
        if nutrition_response.status_code != 200:
            return {"error": "Nutrition failed", "details": nutrition_response.text}

        nutrition = nutrition_response.json().get("nutrition", {})
        glucose_response = requests.post(
            f"{GLUCOSE_MONITOR_URL}/predict-glucose",
            data={
                "protein_pct": nutrition.get("protein_pct", 0),
                "fat_pct": nutrition.get("fat_pct", 0),
                "carbs_pct": nutrition.get("carbs_pct", 0),
                "sugar_risk": nutrition.get("sugar_risk", 0),
                "refined_carb": nutrition.get("refined_carb", 0),
                "meal_category": meal_category
            },
            files={
                "bio_file": ("bio.csv", bio_bytes, "text/csv"),
                "micro_file": ("micro.csv", micro_bytes, "text/csv")
            }
        )

        if glucose_response.status_code != 200:
            return {"error": "glucose prediction failed", "details": glucose_response.text}

        glucose = glucose_response.json()

        # === Set Prometheus Metric ===
        if "glucose_spike_60min" in glucose:
            PREDICTION_VALUE.set(glucose.get("glucose_spike_60min", 0))
        
        # Save data to the database if user_id is provided
        database_info = {}
        if user_id:
            # Save bio data if provided and not using saved data
            if bio_file and not use_saved_bio:
                # 1) Read the uploaded bio CSV into a DataFrame
                bio_file.file.seek(0)
                bio_df = pd.read_csv(io.BytesIO(bio_bytes))
                
                if len(bio_df) >= 1:
                    # 2) Extract headers and values from the first (and only) row
                    raw_headers = bio_df.columns.tolist()
                    values      = bio_df.iloc[0].tolist()

                    # 3) Prepare an empty clinical_data dict
                    clinical_data = {
                        'clinical_age': None,
                        'clinical_weight': None,
                        'clinical_height': None,
                        'clinical_bmi': None,
                        'clinical_fasting_glucose': None,
                        'clinical_fasting_insulin': None,
                        'clinical_hba1c': None,
                        'clinical_homa_ir': None,
                        'clinical_gender': None
                    }

                    # 4) Normalize headers for matching
                    clean_headers = [
                        h.strip().lower()
                        .replace(' ', '_')
                        .replace('-', '_')
                        .replace('%', '')
                        for h in raw_headers
                    ]

                    # 5) Define mapping patterns → target fields
                    field_mapping = {
                        'age':                     'clinical_age',
                        'weight':                  'clinical_weight',
                        'height':                  'clinical_height',
                        'bmi':                     'clinical_bmi',
                        'fasting_glucose':         'clinical_fasting_glucose',
                        'fasting_insulin':         'clinical_fasting_insulin',
                        'hba1c':                   'clinical_hba1c',
                        'homa_ir':                 'clinical_homa_ir',
                        'gender':                  'clinical_gender',
                    }

                    # 6) Fill clinical_data by pattern-matching normalized headers
                    for i, norm in enumerate(clean_headers):
                        for pattern, field in field_mapping.items():
                            if pattern in norm:
                                clinical_data[field] = values[i]

                    # 7) Cast any numpy types to native Python types
                    for key, val in clinical_data.items():
                        if hasattr(val, 'item'):
                            clinical_data[key] = val.item()

                    # 8) Save to database
                    success, msg = save_clinical_data(user_id, clinical_data)
                    database_info["bio_saved"]   = success
                    database_info["bio_message"] = msg

            # Save microbiome data if provided and not using saved data
            if micro_file and not use_saved_micro:
                # Parse the microbiome file to extract bacteria data
                micro_file.file.seek(0)  # Reset file pointer
                micro_df = pd.read_csv(io.BytesIO(micro_bytes))
                
                if len(micro_df) >= 1:
                    # Get first row values and convert to string of 0s and 1s
                    bacteria_values = micro_df.iloc[0].astype(str).values
                    bacteria_string = ''.join([val.strip() for val in bacteria_values])
                    
                    # Save to database
                    bact_id, msg = save_bacteria_data(user_id, bacteria_string)
                    database_info["microbiome_saved"] = (bact_id is not None)
                    database_info["microbiome_message"] = msg
                    database_info["bact_id"] = bact_id

            # Save meal and glucose prediction data
            meal_data = {
                'protein_pct': nutrition.get('protein_pct'),
                'carbs_pct': nutrition.get('carbs_pct'),
                'fat_pct': nutrition.get('fat_pct'),
                'sugar_risk': nutrition.get('sugar_risk'),
                'refined_carb': bool(nutrition.get('refined_carb', False)),  # CAST TO BOOLEAN
                'meal_category': meal_category,
                'glucose_spike_30min': glucose.get('glucose_spike_30min'),
                'glucose_spike_60min': glucose.get('glucose_spike_60min')
            }
            
            meal_id, msg = save_meal_data(user_id, meal_data)
            database_info["meal_saved"] = (meal_id is not None)
            database_info["meal_message"] = msg
            database_info["meal_id"] = meal_id

        # Return combined results
        result = {
            "nutrition": nutrition,
            "glucose_prediction": glucose,
            "database_info": database_info if user_id else None
        }

        return result

    except Exception as e:
        return {"error": f"Internal server error: {str(e)}"}