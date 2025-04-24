# RUN: uvicorn app:app --host 0.0.0.0 --port 8000

from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import requests
import os
from pydantic import BaseModel

# Database setup
DATABASE_URL = "sqlite:///./nutrition_app.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create database directory if it doesn't exist
os.makedirs(os.path.dirname(DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)

# User model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for request/response
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    
class UserLogin(BaseModel):
    username: str
    password: str
    
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    
    class Config:
        orm_mode = True

app = FastAPI()

# User sign-up endpoint
@app.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    db_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
        
    # Create new user - store password as plain text (not secure, but simple for now)
    db_user = User(
        email=user.email,
        username=user.username,
        password=user.password  # In a real app, you'd hash this!
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

# User sign-in endpoint
@app.post("/signin")
async def signin(user_login: UserLogin, db: Session = Depends(get_db)):
    """Sign in a user"""
    # Find the user by username
    db_user = db.query(User).filter(User.username == user_login.username).first()
    
    # Check if user exists and password matches
    if not db_user or db_user.password != user_login.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Return user info on successful login
    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "message": "Login successful"
    }

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
        # === Read input files ===
        image_bytes = image.file.read()
        bio_bytes = bio_file.file.read()
        micro_bytes = micro_file.file.read()

        # === STEP 1: Analyze Meal ===
        analyze_response = requests.post(
            "http://localhost:8000/analyze-meal",
            files={"image": ("meal.jpg", image_bytes, image.content_type)}
        )
        if analyze_response.status_code != 200:
            return {"error": "analyze-meal failed", "details": analyze_response.text}

        analyze = analyze_response.json()
        nutrition = analyze.get("nutrition", {})

        # === STEP 2: Predict Glucose Spike ===
        glucose_response = requests.post(
            "http://localhost:8004/predict-glucose",
            data={
                "protein_pct": nutrition.get("protein_pct", 0),
                "fat_pct": nutrition.get("fat_pct", 0),
                "carbs_pct": nutrition.get("carbs_pct", 0),
                "sugar_risk": nutrition.get("sugar_risk", 0),
                "refined_carb": nutrition.get("refined_carb", 0),
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
            "caption": analyze.get("caption"),
            "nutrition": nutrition,
            "glucose_prediction": glucose
        }

    except Exception as e:
        return {"error": f"Internal server error: {str(e)}"}