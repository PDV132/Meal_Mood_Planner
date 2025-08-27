from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import tempfile
import os
import base64
from datetime import datetime, timedelta
import asyncio
import logging

# Import our enhanced components
#from vector_meal_engine import VectorMealEngine

# Import your new AgenticCore
from agentic_core import AgenticCore

from enhanced_mood_detector import EnhancedMoodDetector
from enhanced_meal_suggester import EnhancedMealSuggester
from speech_to_text import transcribe_audio
from text_to_speech import convert_text_to_speech



# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define mood-based meal suggestion model
class MoodRequest(BaseModel):
    mood: str

class MealSuggestion(BaseModel):
    name: str
    reason: str

# Initialize FastAPI app
app = FastAPI(
    title="🧠 AI Mood Meal Assistant API",
    description="Advanced AI-powered meal recommendations based on mood analysis with vector search and small language models",
    version="2.0.0"
)


# Define the data model for the request
class MoodText(BaseModel):
    text: str

# Create an instance of your FastAPI app
app = FastAPI()

# Create an instance of your AgenticCore
# This will be done once when the server starts, so it's ready to handle requests.
agentic_core_instance = AgenticCore()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
try:
    logger.info("Initializing AI components...")
    # vector_engine = VectorMealEngine()  # Assuming VectorMealEngine is defined elsewhere
    mood_detector = EnhancedMoodDetector()
    meal_suggester = EnhancedMealSuggester()
    logger.info("All AI components initialized successfully!")
except Exception as e:
    logger.error(f"Error initializing AI components: {e}")
    vector_engine = None
    mood_detector = None
    meal_suggester = None

# Mood-based meal suggestions
MOOD_MEALS = {
    "happy": [
        {"name": "Colorful Mediterranean Salad", "reason": "Fresh and vibrant like your mood!"},
        {"name": "Grilled Chicken with Mango Salsa", "reason": "Light and uplifting, perfect for your positive energy."}
    ],
    "sad": [
        {"name": "Comforting Mac and Cheese", "reason": "A warm hug in a bowl to lift your spirits."},
        {"name": "Homemade Chicken Soup", "reason": "Soothing and nourishing for emotional comfort."}
    ],
    "tired": [
        {"name": "Energy-Boosting Buddha Bowl", "reason": "Packed with nutrients to revitalize you."},
        {"name": "Quinoa Power Bowl with Avocado", "reason": "Sustained energy release to combat fatigue."}
    ],
    "excited": [
        {"name": "Spicy Thai Curry", "reason": "Matches your energetic mood with bold flavors!"},
        {"name": "Sushi Rainbow Roll", "reason": "Fun and festive like your current state."}
    ],
    "neutral": [
        {"name": "Balanced Grain Bowl", "reason": "A well-rounded meal for your balanced mood."},
        {"name": "Grilled Salmon with Vegetables", "reason": "Classic and satisfying without being overwhelming."}
    ]
}

# Pydantic models
class TextMoodRequest(BaseModel):
    text: str
    user_id: str = "default"

class MoodRequest(BaseModel):
    mood1: str
    mood2: str
    user_id: str = "default"

class PreferencesRequest(BaseModel):
    user_id: str
    dietary_restrictions: List[str] = []
    cultural_preferences: List[str] = []

class RatingRequest(BaseModel):
    user_id: str
    mood_combo: List[str]
    meal_name: str
    rating: int

class MoodSuggestionRequest(BaseModel):
    mood: str
    user_id: str = "default"

@app.post("/api/suggest/meals")
async def suggest_meals(request: MoodRequest):
    """Suggest meals based on the detected mood"""
    try:
        mood = request.mood.lower()
        if mood in MOOD_MEALS:
            return MOOD_MEALS[mood]
        else:
            # Default to neutral suggestions if mood not recognized
            return MOOD_MEALS["neutral"]
    except Exception as e:
        logger.error(f"Error suggesting meals: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    partial_text: str
    limit: int = 10

# In-memory storage for reminders (in production, use a database)
meal_reminders = {}
user_last_meal = {}



@app.get("/")
def read_root():
    return {"message": "Welcome to the Agentic Mood Meal Planner Backend!"}

# This is the new endpoint for your agentic functionality
@app.post("/agentic-meal-suggestion")
async def get_agentic_suggestion(payload: MoodText):
    """
    Endpoint to get a meal suggestion from the agentic AI system.
    The agent will analyze the text, determine the mood, and find a suitable meal.
    """
    try:
        # Call the run_agent method on your AgenticCore instance
        result = agentic_core_instance.run_agent(payload.text)
        
        # The agent's output is a dictionary, so we return it directly
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "🧠 AI Mood Meal Assistant API",
        "version": "2.0.0",
        "features": [
            "Vector-based meal recommendations using FAISS",
            "Small language model explanations",
            "Sentence transformer embeddings",
            "Audio mood detection",
            "User preference learning",
            "Smart meal reminders"
        ],
        "endpoints": {
            "text_analysis": "/suggest-meal-from-text",
            "mood_selection": "/suggest-meal-from-moods", 
            "audio_analysis": "/suggest-meal-from-audio",
            "preferences": "/set-preferences",
            "rating": "/rate-meal",
            "reminders": "/check-reminders",
            "stats": "/stats"
        }
    }

@app.post("/suggest-meal-from-text")
async def suggest_meal_from_text(request: TextMoodRequest):
    """Get meal suggestion based on text description of mood"""
    try:
        if not vector_engine:
            raise HTTPException(status_code=503, detail="Vector engine not available")
        
        # Detect mood from text using enhanced detector
        mood1, mood2 = mood_detector.detect_mood_from_text(request.text) if mood_detector else ("Calm", "Neutral")
        
        # Get user preferences
        user_prefs = mood_detector.get_user_preferences(request.user_id) if mood_detector else {}
        
        # Get recommendations using vector search
        recommendations = vector_engine.recommend_meals(
            mood_text=request.text,
            mood1=mood1,
            mood2=mood2,
            user_preferences=user_prefs,
            k=1
        )
        
        if not recommendations:
            raise HTTPException(status_code=404, detail="No suitable meals found")
        
        meal = recommendations[0]
        
        # Generate enhanced explanation using small language model
        explanation = meal.get('explanation', 'This meal is recommended based on your current mood and nutritional needs.')
        
        # Convert explanation to speech
        explanation_audio = None
        try:
            audio_bytes = convert_text_to_speech(explanation)
            if audio_bytes:
                explanation_audio = base64.b64encode(audio_bytes).decode('utf-8')
        except Exception as e:
            logger.warning(f"Could not generate audio: {e}")
        
        # Update last meal time
        user_last_meal[request.user_id] = datetime.now()
        
        response = {
            "meal": meal["meal_name"],
            "mood_detected": [mood1, mood2],
            "reason": meal["reason"],
            "benefit": meal["benefit"],
            "calories": meal.get("calories", "N/A"),
            "cultural_theme": meal.get("cultural_theme", "Mixed"),
            "dietary_theme": meal.get("dietary_theme", "General"),
            "similarity_score": meal.get("similarity_score", 0.0),
            "explanation": explanation,
            "confidence": "High" if meal.get("similarity_score", 0) > 0.8 else "Medium"
        }
        
        if explanation_audio:
            response["explanation_audio"] = explanation_audio
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in text mood analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/suggest-meal-from-moods")
async def suggest_meal_from_moods(request: MoodRequest):
    """Get meal suggestion based on selected moods"""
    try:
        if not vector_engine:
            # Fallback to enhanced meal suggester
            if meal_suggester:
                result = meal_suggester.suggest_meal(request.mood1, request.mood2, request.user_id)
                if "error" not in result:
                    user_last_meal[request.user_id] = datetime.now()
                return result
            else:
                raise HTTPException(status_code=503, detail="Meal suggestion service not available")
        
        # Get user preferences
        user_prefs = mood_detector.get_user_preferences(request.user_id) if mood_detector else {}
        
        # Create mood text for vector search
        mood_text = f"feeling {request.mood1.lower()} and {request.mood2.lower()}"
        
        # Get recommendations using vector search
        recommendations = vector_engine.recommend_meals(
            mood_text=mood_text,
            mood1=request.mood1,
            mood2=request.mood2,
            user_preferences=user_prefs,
            k=1
        )
        
        if not recommendations:
            raise HTTPException(status_code=404, detail="No suitable meals found")
        
        meal = recommendations[0]
        
        # Update last meal time
        user_last_meal[request.user_id] = datetime.now()
        
        return {
            "meal": meal["meal_name"],
            "mood_detected": [request.mood1, request.mood2],
            "reason": meal["reason"],
            "benefit": meal["benefit"],
            "calories": meal.get("calories", "N/A"),
            "cultural_theme": meal.get("cultural_theme", "Mixed"),
            "dietary_theme": meal.get("dietary_theme", "General"),
            "similarity_score": meal.get("similarity_score", 0.0),
            "explanation": meal.get("explanation", "This meal is recommended based on your selected moods."),
            "confidence": "High"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in mood-based suggestion: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/suggest-meal-from-audio")
async def suggest_meal_from_audio(audio: UploadFile = File(...), user_id: str = "default"):
    """Get meal suggestion based on audio mood analysis"""
    try:
        if not vector_engine or not mood_detector:
            raise HTTPException(status_code=503, detail="Audio analysis service not available")
        
        # Save uploaded audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            content = await audio.read()
            temp_audio.write(content)
            temp_audio_path = temp_audio.name
        
        try:
            # Transcribe audio to text
            transcribed_text = transcribe_audio(temp_audio_path)
            
            # Detect mood from audio and text
            mood1, mood2 = mood_detector.detect_mood_from_audio(temp_audio_path, transcribed_text)
            
            # Get user preferences
            user_prefs = mood_detector.get_user_preferences(user_id)
            
            # Create comprehensive mood text
            mood_text = f"{transcribed_text} feeling {mood1.lower()} and {mood2.lower()}"
            
            # Get recommendations using vector search
            recommendations = vector_engine.recommend_meals(
                mood_text=mood_text,
                mood1=mood1,
                mood2=mood2,
                user_preferences=user_prefs,
                k=1
            )
            
            if not recommendations:
                raise HTTPException(status_code=404, detail="No suitable meals found")
            
            meal = recommendations[0]
            
            # Generate enhanced explanation
            explanation = meal.get('explanation', f"Based on your voice analysis, {meal['meal_name']} is perfect for your current {mood1.lower()} and {mood2.lower()} state.")
            
            # Convert explanation to speech
            explanation_audio = None
            try:
                audio_bytes = convert_text_to_speech(explanation)
                if audio_bytes:
                    explanation_audio = base64.b64encode(audio_bytes).decode('utf-8')
            except Exception as e:
                logger.warning(f"Could not generate audio response: {e}")
            
            # Update last meal time
            user_last_meal[user_id] = datetime.now()
            
            response = {
                "meal": meal["meal_name"],
                "mood_detected": [mood1, mood2],
                "transcribed_text": transcribed_text,
                "reason": meal["reason"],
                "benefit": meal["benefit"],
                "calories": meal.get("calories", "N/A"),
                "cultural_theme": meal.get("cultural_theme", "Mixed"),
                "dietary_theme": meal.get("dietary_theme", "General"),
                "similarity_score": meal.get("similarity_score", 0.0),
                "explanation": explanation,
                "confidence": "High" if meal.get("similarity_score", 0) > 0.7 else "Medium"
            }
            
            if explanation_audio:
                response["explanation_audio"] = explanation_audio
            
            return response
            
        finally:
            # Clean up temporary file
            os.unlink(temp_audio_path)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in audio mood analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/set-preferences")
async def set_preferences(request: PreferencesRequest):
    """Set user dietary and cultural preferences"""
    try:
        if mood_detector:
            mood_detector.set_dietary_restrictions(request.user_id, request.dietary_restrictions)
            mood_detector.set_cultural_preferences(request.user_id, request.cultural_preferences)
        
        if meal_suggester:
            meal_suggester.set_dietary_restrictions(request.user_id, request.dietary_restrictions)
            meal_suggester.set_cultural_preferences(request.user_id, request.cultural_preferences)
        
        return {
            "message": "Preferences updated successfully",
            "user_id": request.user_id,
            "dietary_restrictions": request.dietary_restrictions,
            "cultural_preferences": request.cultural_preferences
        }
        
    except Exception as e:
        logger.error(f"Error setting preferences: {e}")
        raise HTTPException(status_code=500, detail=f"Could not update preferences: {str(e)}")

@app.post("/rate-meal")
async def rate_meal(request: RatingRequest):
    """Rate a meal suggestion for learning"""
    try:
        mood_combo = tuple(request.mood_combo)
        
        # Update preferences in mood detector
        if mood_detector:
            mood_detector.update_user_preference(
                request.user_id, mood_combo, request.meal_name, request.rating
            )
        
        # Update preferences in meal suggester
        if meal_suggester:
            meal_suggester.update_user_preference(
                request.user_id, mood_combo, request.meal_name, request.rating
            )
        
        # Update vector engine with feedback
        if vector_engine:
            mood_context = f"feeling {mood_combo[0].lower()} and {mood_combo[1].lower()}"
            vector_engine.update_meal_feedback(request.meal_name, request.rating, mood_context)
        
        return {
            "message": "Rating recorded successfully",
            "meal_name": request.meal_name,
            "rating": request.rating,
            "learning_updated": True
        }
        
    except Exception as e:
        logger.error(f"Error recording rating: {e}")
        raise HTTPException(status_code=500, detail=f"Could not record rating: {str(e)}")

@app.get("/mood-suggestions")
async def get_mood_suggestions(partial_text: str, limit: int = 10):
    """Get mood suggestions for autocomplete"""
    try:
        if vector_engine:
            suggestions = vector_engine.get_mood_suggestions(partial_text, limit)
        elif meal_suggester:
            suggestions = meal_suggester.get_mood_suggestions(partial_text, limit)
        else:
            suggestions = []
        
        return {"suggestions": suggestions}
        
    except Exception as e:
        logger.error(f"Error getting mood suggestions: {e}")
        return {"suggestions": []}

@app.get("/similar-meals/{meal_name}")
async def get_similar_meals(meal_name: str, limit: int = 5):
    """Get meals similar to a given meal"""
    try:
        if not vector_engine:
            raise HTTPException(status_code=503, detail="Vector search not available")
        
        similar_meals = vector_engine.get_similar_meals(meal_name, k=limit)
        
        return {
            "meal_name": meal_name,
            "similar_meals": [
                {
                    "name": meal["meal_name"],
                    "similarity_score": meal["similarity_score"],
                    "reason": meal["reason"],
                    "cultural_theme": meal.get("cultural_theme", "Mixed")
                }
                for meal in similar_meals
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding similar meals: {e}")
        raise HTTPException(status_code=500, detail=f"Could not find similar meals: {str(e)}")

@app.get("/check-reminders/{user_id}")
async def check_reminders(user_id: str):
    """Check if user needs meal reminders"""
    try:
        current_time = datetime.now()
        
        # Check last meal time
        if user_id in user_last_meal:
            last_meal_time = user_last_meal[user_id]
            time_since_meal = current_time - last_meal_time
            
            if time_since_meal > timedelta(hours=3):
                # Generate a gentle reminder with meal suggestion
                if vector_engine:
                    # Suggest a comfort meal for reminder
                    recommendations = vector_engine.recommend_meals(
                        mood_text="need nourishment and energy",
                        mood1="Tired",
                        mood2="Hungry",
                        k=1
                    )
                    
                    suggested_meal = recommendations[0]["meal_name"] if recommendations else "a nutritious meal"
                else:
                    suggested_meal = "a healthy meal"
                
                return {
                    "needs_reminder": True,
                    "hours_since_last_meal": time_since_meal.total_seconds() / 3600,
                    "message": f"It's been {int(time_since_meal.total_seconds() / 3600)} hours since your last meal. Time to nourish your body!",
                    "suggested_meal": suggested_meal,
                    "reminder_type": "overdue"
                }
        
        return {
            "needs_reminder": False,
            "message": "You're doing great with your meal timing!",
            "reminder_type": "none"
        }
        
    except Exception as e:
        logger.error(f"Error checking reminders: {e}")
        return {"needs_reminder": False, "error": str(e)}

@app.get("/stats")
async def get_stats():
    """Get system statistics and health"""
    try:
        stats = {
            "system_status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "vector_engine": vector_engine is not None,
                "mood_detector": mood_detector is not None,
                "meal_suggester": meal_suggester is not None
            },
            "active_users": len(user_last_meal),
            "total_reminders_sent": len(meal_reminders)
        }
        
        # Add vector engine stats if available
        if vector_engine:
            vector_stats = vector_engine.get_stats()
            stats["vector_engine_stats"] = vector_stats
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {"system_status": "error", "error": str(e)}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "components_loaded": {
            "vector_engine": vector_engine is not None,
            "mood_detector": mood_detector is not None,
            "meal_suggester": meal_suggester is not None
        }
    }

# Background task for periodic reminders (in production, use Celery or similar)
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks"""
    logger.info("🚀 AI Mood Meal Assistant API started successfully!")
    logger.info("Available endpoints:")
    logger.info("  - POST /agentic-meal-suggestion")
    logger.info("  - POST /suggest-meal-from-text")
    logger.info("  - POST /suggest-meal-from-moods")
    logger.info("  - POST /suggest-meal-from-audio")
    logger.info("  - POST /set-preferences")
    logger.info("  - POST /rate-meal")
    logger.info("  - GET /mood-suggestions")
    logger.info("  - GET /similar-meals/{meal_name}")
    logger.info("  - GET /check-reminders/{user_id}")
    logger.info("  - GET /stats")
    logger.info("  - GET /health")

if __name__ == "__main__":
    uvicorn.run(
        "enhanced_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )