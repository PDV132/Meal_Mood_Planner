from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DietaryPreferences(BaseModel):
    restrictions: List[str] = []  # e.g., ["vegetarian", "gluten-free", "dairy-free"]
    allergies: List[str] = []
    preferred_cuisines: List[str] = []
    disliked_ingredients: List[str] = []
    calories_target: Optional[int] = None
    
class MealTracking(BaseModel):
    last_meal_time: Optional[datetime] = None
    next_meal_reminder: Optional[datetime] = None
    missed_meals_count: int = 0

class UserPreferences(BaseModel):
    user_id: str
    dietary_preferences: DietaryPreferences
    meal_tracking: MealTracking
