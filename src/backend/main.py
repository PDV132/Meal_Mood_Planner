from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import mood_router, meal_router, preferences_router, voice_router
from backend.core import init_ai_components
import asyncio

app = FastAPI(
    title="🧠 AI Mood Meal Assistant API",
    description="Advanced AI-powered meal recommendations based on mood analysis with vector search and small language models",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI components
init_ai_components()

# Include routers
app.include_router(mood_router.router, prefix="/api/mood", tags=["mood"])
app.include_router(meal_router.router, prefix="/api/meals", tags=["meals"])
app.include_router(preferences_router.router, prefix="/api/user", tags=["user"])
app.include_router(voice_router.router, prefix="/api/voice", tags=["voice"])

@app.on_event("startup")
async def startup_event():
    # Start the reminder service
    asyncio.create_task(preferences_router.reminder_service.start_reminder_service())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
