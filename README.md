# 🧠 AI Mood Meal Assistant

An advanced AI-powered meal recommendation system that analyzes your mood through text, voice, and audio to suggest personalized meals. Built with cutting-edge technologies including vector search, FAISS, sentence transformers, and small language models.

## ✨ Features

### 🎯 Core Capabilities
- **Multi-Modal Mood Detection**: Analyze mood through text descriptions, voice recordings, and audio analysis
- **Vector-Based Recommendations**: Uses FAISS and sentence transformers for semantic meal matching
- **Small Language Model Integration**: Generates personalized explanations using DistilGPT-2
- **User Preference Learning**: Adapts recommendations based on your feedback and dietary preferences
- **Smart Reminders**: Sends notifications when you haven't eaten for more than 3 hours
- **Beautiful UI**: Modern, responsive Streamlit interface with animations and gradients

### 🤖 AI Technologies
- **Sentence Transformers**: `all-MiniLM-L6-v2` for semantic embeddings
- **FAISS Vector Search**: Fast similarity search across 500+ meals
- **Small Language Models**: DistilGPT-2 for explanation generation
- **Audio Processing**: Librosa for voice emotion analysis
- **Text-to-Speech**: gTTS for audio responses

### 🍽️ Meal Database
- **500+ Curated Meals** from various cultures
- **Mood-Food Mapping** based on nutritional psychology
- **Cultural Themes**: South Asian, East Asian, Mediterranean, Middle Eastern, Latin American, African, Western Comfort, Fusion
- **Dietary Options**: Vegan, Vegetarian, Gluten-Free, High-Protein, Low-Carb, Comfort Food, Gut-Soothing

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- 4GB+ RAM (for AI models)
- Internet connection (for initial model downloads)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Mood_Meal_Planner
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Download AI models** (automatic on first run)
The system will automatically download:
- Sentence transformer model (~22MB)
- DistilGPT-2 language model (~82MB)
- Emotion classification model (~250MB)

### Running the Application

#### Option 1: Full System (Recommended)

1. **Start the backend server**
```bash
python enhanced_backend.py
```
The API will be available at `http://localhost:8000`

2. **Start the frontend UI** (in a new terminal)
```bash
streamlit run enhanced_app.py
```
The web interface will open at `http://localhost:8501`

#### Option 2: Test Individual Components

**Test Vector Engine**
```bash
python vector_meal_engine.py
```

**Test Mood Detection**
```bash
python enhanced_mood_detector.py
```

## 🎮 Usage Guide

### 1. Text-Based Mood Analysis
1. Open the web interface
2. Describe your current mood in the text area
3. Click "🔍 Analyze My Mood"
4. Get personalized meal recommendations with explanations

### 2. Quick Mood Selection
1. Choose a mood category (Negative, Positive, Neutral)
2. Select primary and secondary moods
3. Click "🎯 Get Quick Suggestion"

### 3. Voice Mood Analysis
1. Click the microphone button
2. Speak naturally about how you're feeling
3. The system analyzes both your words and voice tone
4. Receive audio explanations of recommendations

### 4. Set Preferences
1. Open the sidebar
2. Set dietary restrictions (Vegetarian, Vegan, etc.)
3. Choose cultural preferences
4. Save preferences for personalized recommendations

### 5. Rate Recommendations
1. After receiving a suggestion, rate it 1-5 stars
2. The system learns from your feedback
3. Future recommendations improve based on your preferences

## 🏗️ Architecture

### System Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │────│  FastAPI Backend │────│ Vector Engine   │
│   (Frontend)    │    │   (API Layer)    │    │ (FAISS + ST)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                       ┌────────┴────────┐
                       │                 │
                ┌──────▼──────┐   ┌──────▼──────┐
                │ Mood        │   │ Meal        │
                │ Detector    │   │ Suggester   │
                └─────────────┘   └─────────────┘
```

### Key Files

- **`enhanced_app.py`**: Beautiful Streamlit frontend with modern UI
- **`enhanced_backend.py`**: FastAPI server with all endpoints
- **`vector_meal_engine.py`**: Core AI engine with FAISS and sentence transformers
- **`enhanced_mood_detector.py`**: Multi-modal mood detection system
- **`enhanced_meal_suggester.py`**: Comprehensive meal recommendation logic
- **`meal.json`**: Curated database of 500+ mood-mapped meals

### AI Pipeline

1. **Input Processing**: Text/Audio → Preprocessing → Feature Extraction
2. **Mood Detection**: Transformers → Emotion Classification → Mood Mapping
3. **Vector Search**: Query Embedding → FAISS Search → Similarity Ranking
4. **Recommendation**: Preference Filtering → Ranking → Selection
5. **Explanation**: Small LM → Text Generation → Audio Synthesis

## 🔧 API Endpoints

### Core Endpoints
- `POST /suggest-meal-from-text` - Text-based mood analysis
- `POST /suggest-meal-from-moods` - Direct mood selection
- `POST /suggest-meal-from-audio` - Voice mood analysis
- `POST /set-preferences` - User preference management
- `POST /rate-meal` - Feedback and learning

### Utility Endpoints
- `GET /mood-suggestions` - Autocomplete for moods
- `GET /similar-meals/{meal_name}` - Find similar meals
- `GET /check-reminders/{user_id}` - Meal reminder system
- `GET /stats` - System statistics
- `GET /health` - Health check

### Example API Usage

```python
import requests

# Text-based recommendation
response = requests.post("http://localhost:8000/suggest-meal-from-text", 
                        json={"text": "I'm feeling anxious and tired", "user_id": "user123"})
print(response.json())

# Set preferences
requests.post("http://localhost:8000/set-preferences", 
              json={"user_id": "user123", 
                   "dietary_restrictions": ["Vegetarian"], 
                   "cultural_preferences": ["South Asian"]})
```

## 🎨 UI Features

### Modern Design Elements
- **Gradient Backgrounds**: Beautiful color transitions
- **Smooth Animations**: Hover effects and loading spinners
- **Responsive Layout**: Works on desktop and mobile
- **Interactive Charts**: Mood history visualization
- **Audio Integration**: Voice input and audio responses

### User Experience
- **Real-time Feedback**: Instant mood analysis
- **Progress Indicators**: Loading states and progress bars
- **Contextual Help**: Tooltips and guidance
- **Accessibility**: Screen reader friendly
- **Dark/Light Themes**: Automatic theme detection

## 🧪 Advanced Features

### Vector Search Capabilities
```python
# Find similar meals
similar_meals = vector_engine.get_similar_meals("Lentil Soup", k=5)

# Custom mood queries
recommendations = vector_engine.recommend_meals(
    mood_text="feeling overwhelmed with work stress",
    mood1="Stressed", 
    mood2="Overwhelmed",
    k=3
)
```

### Learning and Adaptation
- **Feedback Integration**: Ratings update vector embeddings
- **Preference Evolution**: System learns from user behavior
- **Contextual Memory**: Remembers past successful recommendations

### Performance Optimizations
- **Model Caching**: Pre-computed embeddings for fast search
- **Batch Processing**: Efficient vector operations
- **Index Persistence**: FAISS index saved to disk
- **Lazy Loading**: Models loaded on demand

## 🔍 Troubleshooting

### Common Issues

**1. Models not downloading**
```bash
# Manually download models
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

**2. FAISS installation issues**
```bash
# For CPU-only version
pip install faiss-cpu

# For GPU version (if you have CUDA)
pip install faiss-gpu
```

**3. Audio not working**
- Check microphone permissions
- Ensure audio drivers are installed
- Try different audio formats

**4. Memory issues**
- Reduce batch size in vector operations
- Use CPU-only models if GPU memory is limited
- Close other applications

### Performance Tips

1. **First Run**: Initial model downloads may take time
2. **Memory Usage**: ~2GB RAM for full system
3. **Response Time**: ~1-3 seconds for recommendations
4. **Concurrent Users**: Backend supports multiple users

## 📊 System Statistics

The system provides detailed statistics:

```json
{
  "total_meals": 500,
  "embedding_dimension": 384,
  "mood_categories": 50+,
  "model_info": {
    "sentence_transformer": "all-MiniLM-L6-v2",
    "language_model": "distilgpt2",
    "embedding_model_size": "22MB",
    "language_model_size": "82MB"
  }
}
```

## 🤝 Contributing

We welcome contributions! Areas for improvement:

1. **New Meal Data**: Add more culturally diverse meals
2. **Mood Categories**: Expand emotion detection capabilities
3. **UI Enhancements**: Improve user experience
4. **Performance**: Optimize AI model inference
5. **Features**: Add new recommendation algorithms

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Hugging Face**: For transformer models and sentence-transformers
- **Facebook AI**: For FAISS vector search library
- **Streamlit**: For the beautiful web framework
- **FastAPI**: For the high-performance API framework
- **OpenAI**: For inspiration in AI-powered applications

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation at `http://localhost:8000/docs`
3. Create an issue in the repository

---

**Built with ❤️ using cutting-edge AI technologies**

*Transform your mood into the perfect meal with AI-powered recommendations!*
