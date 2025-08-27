from datetime import datetime, timedelta
import asyncio
from typing import Dict
from .models.user_preferences import UserPreferences

class MealReminderService:
    def __init__(self):
        self.users: Dict[str, UserPreferences] = {}
        self.reminder_threshold = timedelta(hours=3)
        
    async def start_reminder_service(self):
        while True:
            current_time = datetime.now()
            for user_id, preferences in self.users.items():
                last_meal = preferences.meal_tracking.last_meal_time
                if last_meal:
                    time_since_meal = current_time - last_meal
                    if time_since_meal > self.reminder_threshold:
                        await self.send_reminder(user_id)
                        preferences.meal_tracking.missed_meals_count += 1
            await asyncio.sleep(300)  # Check every 5 minutes
    
    async def send_reminder(self, user_id: str):
        # TODO: Implement your preferred notification method here
        # This could be email, push notification, SMS, etc.
        print(f"REMINDER: It's been over 3 hours since your last meal! User: {user_id}")
    
    def update_meal_time(self, user_id: str):
        if user_id in self.users:
            self.users[user_id].meal_tracking.last_meal_time = datetime.now()
            self.users[user_id].meal_tracking.missed_meals_count = 0
    
    def add_user(self, user_preferences: UserPreferences):
        self.users[user_preferences.user_id] = user_preferences
