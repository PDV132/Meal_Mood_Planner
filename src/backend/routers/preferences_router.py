from fastapi import APIRouter, HTTPException
from typing import List
from ..models.user_preferences import UserPreferences, DietaryPreferences
from ..services.reminder_service import MealReminderService

router = APIRouter()
reminder_service = MealReminderService()

@router.post("/preferences")
async def set_preferences(preferences: UserPreferences):
    reminder_service.add_user(preferences)
    return {"status": "success", "message": "Preferences updated successfully"}

@router.get("/preferences/{user_id}")
async def get_preferences(user_id: str):
    if user_id not in reminder_service.users:
        raise HTTPException(status_code=404, detail="User preferences not found")
    return reminder_service.users[user_id]

@router.post("/meal-logged/{user_id}")
async def log_meal(user_id: str):
    if user_id not in reminder_service.users:
        raise HTTPException(status_code=404, detail="User not found")
    reminder_service.update_meal_time(user_id)
    return {"status": "success", "message": "Meal time logged successfully"}
