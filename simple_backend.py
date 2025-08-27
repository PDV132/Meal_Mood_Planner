
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from typing import Dict, List

app = FastAPI(title="Simple AI Mood Meal Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextMoodRequest(BaseModel):
    text: str
    user_id: str = "default"

class MoodRequest(BaseModel):
    mood1: str
    mood2: str
    user_id: str = "default"

# Load meal data
try:
    with open("meal.json", "r") as f:
        meals = json.load(f)
except:
    meals = [
        {
            "meal_name": "Comfort Soup",
            "mood_1": "Sad",
            "mood_2": "Tired",
            "reason": "Warm and comforting",
            "benefit": "Provides warmth and nutrition",
            "calories": 200,
            "cultural_theme": "Comfort Food",
            "dietary_theme": "General"
        }
    ]

@app.get("/")
async def root():
    return {"message": "Simple AI Mood Meal Assistant API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "meals_loaded": len(meals)}

@app.post("/suggest-meal-from-text")
async def suggest_meal_from_text(request: TextMoodRequest):
    # Simple mood detection
    text_lower = request.text.lower()
    if "sad" in text_lower or "down" in text_lower:
        mood1, mood2 = "Sad", "Tired"
    elif "anxious" in text_lower or "nervous" in text_lower:
        mood1, mood2 = "Anxious", "Restless"
    else:
        mood1, mood2 = "Calm", "Neutral"
    
    # Find matching meal
    for meal in meals:
        if meal.get("mood_1") == mood1 or meal.get("mood_2") == mood2:
            return {
                "meal": meal["meal_name"],
                "mood_detected": [mood1, mood2],
                "reason": meal["reason"],
                "benefit": meal["benefit"],
                "calories": meal.get("calories", "N/A"),
                "cultural_theme": meal.get("cultural_theme", "Mixed"),
                "explanation": f"Based on your mood, {meal['meal_name']} is recommended because {meal['reason']}."
            }
    
    # Fallback
    return {
        "meal": meals[0]["meal_name"],
        "mood_detected": [mood1, mood2],
        "reason": meals[0]["reason"],
        "benefit": meals[0]["benefit"],
        "calories": meals[0].get("calories", "N/A"),
        "cultural_theme": meals[0].get("cultural_theme", "Mixed"),
        "explanation": "A comforting meal to help with your current mood."
    }

@app.post("/suggest-meal-from-moods")
async def suggest_meal_from_moods(request: MoodRequest):
    # Find matching meal
    for meal in meals:
        if meal.get("mood_1") == request.mood1 or meal.get("mood_2") == request.mood2:
            return {
                "meal": meal["meal_name"],
                "reason": meal["reason"],
                "benefit": meal["benefit"],
                "calories": meal.get("calories", "N/A"),
                "cultural_theme": meal.get("cultural_theme", "Mixed")
            }
    
    # Fallback
    return {
        "meal": meals[0]["meal_name"],
        "reason": meals[0]["reason"],
        "benefit": meals[0]["benefit"],
        "calories": meals[0].get("calories", "N/A"),
        "cultural_theme": meals[0].get("cultural_theme", "Mixed")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
