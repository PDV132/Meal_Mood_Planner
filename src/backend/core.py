import json
import os
from pathlib import Path
from typing import Dict

from ai_modules.vector_meal_engine import VectorMealEngine
from ai_modules.meal_suggester import MealSuggester

# Global instances
_meal_engine = None
_meal_suggester = None

def init_ai_components() -> None:
    """Initialize AI components on server startup"""
    global _meal_engine, _meal_suggester
    
    # Initialize meal engine
    _meal_engine = VectorMealEngine()
    
    # Load meal data
    # Try looking in the backend/data directory
    data_path = Path(__file__).parent / "data" / "meals.json"
    if not data_path.exists():
        # Try looking in the src/data directory
        data_path = Path(__file__).parent.parent / "data" / "meals.json"
        if not data_path.exists():
            raise FileNotFoundError(f"Meals data file not found at {data_path}")
    
    with open(data_path) as f:
        meals_data = json.load(f)
        if "meals" in meals_data:
            _meal_engine.load_meals(meals_data["meals"])
        else:
            _meal_engine.load_meals(meals_data)
        
    # Initialize meal suggester
    _meal_suggester = MealSuggester(_meal_engine)
    
def get_meal_suggester() -> MealSuggester:
    """Get the global meal suggester instance"""
    if _meal_suggester is None:
        raise RuntimeError(
            "AI components not initialized. Call init_ai_components() first."
        )
    return _meal_suggester
