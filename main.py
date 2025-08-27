from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from datetime import datetime, timedelta
import requests
import base64
import io
import soundfile as sf

# Custom Modules
from speech_to_text import transcribe_audio
from mood_detector import detect_mood_from_text
from meal_loader import load_meals
from meal_agent import explain_meal
from meal_logger import log_meal, get_last_meal
from text_to_speech import convert_text_to_speech

app = FastAPI()
meals = load_meals()

# Input model for text
class MoodText(BaseModel):
    text: str

def get_meal_suggestion_logic(text: str):
    """Core logic for meal suggestion to be reused by text and audio routes."""
    mood_1, mood_2 = detect_mood_from_text(text)

    # Find a matching meal
    best_meal = next(
        (meal for meal in meals if meal["mood_1"] == mood_1 and meal["mood_2"] == mood_2),
        None
    )

    if not best_meal:
        return {"error": "No meal found for the detected mood."}

    # Generate explanation using LangChain/GPT
    explanation_text = explain_meal(mood_1, mood_2, best_meal)
    
    # Simulate user ID and log meal
    user = "user_001"
    log_meal(user, best_meal["meal_name"])

    # Check if a reminder is needed for "Tired" mood
    if "Tired" in [mood_1, mood_2]:
        last_meal = get_last_meal(user)
        if not last_meal or datetime.utcnow() - datetime.fromisoformat(last_meal["timestamp"]) > timedelta(hours=4):
            try:
                requests.post("http://localhost:5678/webhook-tired", json={
                    "user": user,
                    "mood": [mood_1, mood_2],
                    "meal": best_meal["meal_name"]
                })
            except Exception as e:
                print(f"Failed to send to n8n: {e}")

    return {
        "mood_detected": [mood_1, mood_2],
        "meal": best_meal["meal_name"],
        "reason": best_meal["reason"],
        "benefit": best_meal["benefit"],
        "explanation": explanation_text
    }

@app.post("/suggest-meal-from-text")
def suggest_meal_from_text_endpoint(payload: MoodText):
    return get_meal_suggestion_logic(payload.text)

@app.post("/suggest-meal-from-audio")
async def suggest_meal_from_audio_endpoint(audio: UploadFile = File(...)):
    # Read audio file into an in-memory buffer
    audio_bytes = await audio.read()
    buffer = io.BytesIO(audio_bytes)
    
    # Save buffer to a temporary file path for transcription
    temp_path = f"temp_{audio.filename}"
    with open(temp_path, "wb") as f:
        f.write(buffer.getvalue())

    # Transcribe audio to text
    transcribed_text = transcribe_audio(temp_path)

    if not transcribed_text or "Could not process" in transcribed_text:
        return {"error": "Could not understand the audio."}
        
    # Get meal suggestion based on transcribed text
    result = get_meal_suggestion_logic(transcribed_text)

    if "error" in result:
        return result
        
    # Convert the explanation text to audio
    explanation_audio_bytes = convert_text_to_speech(result["explanation"])
    
    # Encode the audio bytes to base64 to send as JSON
    result["explanation_audio"] = base64.b64encode(explanation_audio_bytes).decode('utf-8')
    
    return result