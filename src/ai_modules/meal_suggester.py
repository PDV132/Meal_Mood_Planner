from transformers import pipeline
from typing import Dict, List, Optional
from .vector_meal_engine import VectorMealEngine

class MealSuggester:
    def __init__(self, meal_engine: VectorMealEngine):
        self.meal_engine = meal_engine
        self.explanation_generator = pipeline(
            "text-generation",
            model="distilgpt2",
            device=-1
        )
        
        # Mood to meal type mapping
        self.mood_meal_preferences = {
            "happy": ["energizing", "colorful", "celebratory"],
            "sad": ["comforting", "warm", "nurturing"],
            "stressed": ["calming", "soothing", "simple"],
            "energetic": ["light", "refreshing", "protein-rich"],
            "tired": ["energizing", "nutritious", "easy-to-prepare"],
            "hungry": ["satisfying", "hearty", "filling"],
            "cozy": ["warm", "comforting", "homestyle"]
        }
        
    def suggest_meals(
        self, 
        mood: str,
        dietary_preferences: Optional[List[str]] = None,
        k: int = 5
    ) -> List[Dict]:
        """
        Suggest meals based on mood and preferences
        Returns list of meal recommendations
        """
        # Create mood-based query
        mood_preferences = self.mood_meal_preferences.get(
            mood, ["balanced", "nutritious"]
        )
        query = f"{mood} mood: {' '.join(mood_preferences)}"
        
        if dietary_preferences:
            query += f" {' '.join(dietary_preferences)}"
            
        # Get similar meals
        similar_meals = self.meal_engine.find_similar_meals(query, k)
        
        return [meal for meal, _ in similar_meals]
        
    def generate_explanation(
        self,
        mood: str,
        meal: Dict
    ) -> str:
        """Generate natural language explanation for meal suggestion"""
        prompt = f"""
        For someone feeling {mood}, {meal['name']} is a great choice because:
        - It's a {meal['cuisine_type']} dish that
        """
        
        # Generate explanation
        explanation = self.explanation_generator(
            prompt,
            max_length=150,
            num_return_sequences=1,
            temperature=0.7
        )[0]["generated_text"]
        
        # Clean and format explanation
        explanation = explanation.replace(prompt, "").strip()
        explanation = f"This {meal['cuisine_type']} dish is perfect for your {mood} mood. {explanation}"
        
        return explanation
