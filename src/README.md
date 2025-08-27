# AI Mood Meal Assistant

This is an advanced AI-powered meal recommendation system that analyzes your mood through text and voice to suggest personalized meals.

## Project Structure

```
src/
├── frontend/           # Streamlit web interface
│   └── app.py         # Main Streamlit application
├── backend/           # FastAPI backend server
│   ├── main.py       # FastAPI application entry point
│   ├── core.py       # Core initialization and setup
│   ├── utils.py      # Utility functions
│   └── routers/      # API route handlers
│       ├── mood_router.py    # Mood analysis endpoints
│       └── meal_router.py    # Meal-related endpoints
├── ai_modules/       # AI components
│   ├── vector_meal_engine.py  # Vector search for meals
│   ├── mood_detector.py       # Mood analysis
│   └── meal_suggester.py      # Meal recommendation
└── data/            # Data files
    └── meals.json   # Meal database
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the backend server:
```bash
cd src/backend
uvicorn main:app --reload
```

4. Start the frontend:
```bash
cd src/frontend
streamlit run app.py
```

## Features

- Mood analysis through text and voice input
- Vector-based meal recommendations using FAISS
- Personalized explanations using DistilGPT-2
- Beautiful Streamlit UI
- RESTful API with FastAPI

## Technologies

- Frontend: Streamlit
- Backend: FastAPI
- AI: Sentence Transformers, FAISS, Transformers
- Database: JSON (can be extended to other databases)

## License

MIT
