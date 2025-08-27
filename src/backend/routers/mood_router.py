from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
from datetime import datetime
from ai_modules.mood_detector import EnhancedMoodDetector
from backend.core import get_meal_suggester

router = APIRouter()
mood_detector = EnhancedMoodDetector()

class MoodText(BaseModel):
    text: str

class AudioData(BaseModel):
    audio_data: str  # Base64 encoded audio data

@router.post("/text")
async def analyze_mood_text(mood_input: MoodText) -> Dict:
    """Analyze mood from text and get meal recommendations"""
    try:
        # Detect mood
        detected_mood = mood_detector.get_primary_mood(
            mood_input.text,
            {"time": datetime.now()}
        )
        
        # Get meal suggestions
        meal_suggester = get_meal_suggester()
        meals = meal_suggester.suggest_meals(detected_mood)
        
        if not meals:
            raise HTTPException(
                status_code=404,
                detail="No suitable meals found"
            )
            
        # Get first recommendation and explanation
        recommended_meal = meals[0]
        explanation = meal_suggester.generate_explanation(
            detected_mood,
            recommended_meal
        )
        
        return {
            "detected_mood": detected_mood,
            "meal_recommendation": recommended_meal,
            "explanation": explanation
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@router.post("/voice")
async def analyze_mood_voice(audio_data: AudioData) -> Dict:
    """Analyze mood from voice recording and get meal recommendations"""
    try:
        # Process audio data (implement speech-to-text later)
        # For now, return error
        raise HTTPException(
            status_code=501,
            detail="Voice analysis not yet implemented"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing audio: {str(e)}"
        )
