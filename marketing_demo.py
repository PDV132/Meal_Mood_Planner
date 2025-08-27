import streamlit as st
import json
import random
import time
from datetime import datetime
import plotly.express as px
import pandas as pd

# Configure page for marketing demo
st.set_page_config(
    page_title="🧠 AI Mood Meal Assistant - Demo",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for marketing demo
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Custom font */
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Hero section */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        opacity: 0.9;
        margin-bottom: 2rem;
    }
    
    .hero-features {
        display: flex;
        justify-content: center;
        gap: 2rem;
        flex-wrap: wrap;
        margin-top: 2rem;
    }
    
    .feature-badge {
        background: rgba(255,255,255,0.2);
        padding: 0.5rem 1rem;
        border-radius: 25px;
        backdrop-filter: blur(10px);
        font-weight: 500;
    }
    
    /* Demo cards */
    .demo-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid #667eea;
        transition: transform 0.3s ease;
    }
    
    .demo-card:hover {
        transform: translateY(-5px);
    }
    
    /* Recommendation display */
    .recommendation {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 15px 35px rgba(79, 172, 254, 0.3);
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .meal-name {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    .meal-details {
        background: rgba(255,255,255,0.1);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        backdrop-filter: blur(10px);
    }
    
    /* Stats section */
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 2rem 0;
        flex-wrap: wrap;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        min-width: 150px;
        margin: 0.5rem;
        box-shadow: 0 8px 25px rgba(168, 237, 234, 0.3);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2d3748;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #4a5568;
        margin-top: 0.5rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* Loading animation */
    .loading {
        text-align: center;
        padding: 2rem;
    }
    
    .spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        animation: spin 1s linear infinite;
        margin: 0 auto 1rem;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Mood emoji */
    .mood-emoji {
        font-size: 4rem;
        text-align: center;
        margin: 1rem 0;
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
</style>
""", unsafe_allow_html=True)

# Load sample meal data
@st.cache_data
def load_demo_meals():
    return [
        {
            "meal_name": "Lentil Soup",
            "mood_1": "Sad",
            "mood_2": "Anxious",
            "calories": 280,
            "benefit": "Rich in tryptophan and folate, promoting serotonin production",
            "reason": "Soothing, warm, and easy to digest — evokes comfort in South Asian homes",
            "cultural_theme": "South Asian",
            "dietary_theme": "Vegan"
        },
        {
            "meal_name": "Greek Yogurt Parfait",
            "mood_1": "Restless",
            "mood_2": "Distracted",
            "calories": 320,
            "benefit": "Probiotics and B-vitamins balance energy",
            "reason": "Textural variety calms nervous energy, Mediterranean treat",
            "cultural_theme": "Mediterranean",
            "dietary_theme": "High-Protein"
        },
        {
            "meal_name": "Avocado Toast w/ Pumpkin Seeds",
            "mood_1": "Unfocused",
            "mood_2": "Foggy",
            "calories": 310,
            "benefit": "Healthy fats, zinc, and fiber support cognition",
            "reason": "Crunch and creaminess create a sensory reset",
            "cultural_theme": "Fusion",
            "dietary_theme": "Whole-Food"
        },
        {
            "meal_name": "Kimchi Fried Rice",
            "mood_1": "Anxious",
            "mood_2": "Stressed",
            "calories": 430,
            "benefit": "Fermented foods and fiber support gut mood",
            "reason": "Zingy yet grounding — East Asian comfort with edge",
            "cultural_theme": "East Asian",
            "dietary_theme": "Gut-Soothing"
        },
        {
            "meal_name": "Turmeric Quinoa Pilaf",
            "mood_1": "Stressed",
            "mood_2": "Overwhelmed",
            "calories": 400,
            "benefit": "Anti-inflammatory turmeric calms the nervous system",
            "reason": "Golden, earthy tones provide visual and emotional soothing",
            "cultural_theme": "South Asian",
            "dietary_theme": "Vegan"
        }
    ]

# Hero Section
st.markdown("""
<div class="hero-section">
    <div class="hero-title">🧠 AI Mood Meal Assistant</div>
    <div class="hero-subtitle">Transform your emotions into the perfect meal with cutting-edge AI</div>
    <div class="hero-features">
        <div class="feature-badge">🎯 Vector Search</div>
        <div class="feature-badge">🤖 Small Language Models</div>
        <div class="feature-badge">🔊 Voice Analysis</div>
        <div class="feature-badge">📊 FAISS + Transformers</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Statistics Section
st.markdown("""
<div class="stats-container">
    <div class="stat-card">
        <div class="stat-number">500+</div>
        <div class="stat-label">Curated Meals</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">384</div>
        <div class="stat-label">Vector Dimensions</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">8</div>
        <div class="stat-label">Cultural Cuisines</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">50+</div>
        <div class="stat-label">Mood Categories</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Demo Section
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    <div class="demo-card">
        <h3>🎭 Try the AI Mood Detection</h3>
        <p>Describe how you're feeling and watch our AI analyze your emotions in real-time</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Text input for mood
    user_mood = st.text_area(
        "",
        height=100,
        placeholder="I'm feeling really stressed about work and quite tired from staying up late...",
        help="Describe your current emotional state in detail"
    )
    
    # Demo button
    if st.button("🔍 Analyze My Mood & Get Meal Suggestion", use_container_width=True):
        if user_mood.strip():
            # Show loading animation
            with st.empty():
                st.markdown("""
                <div class="loading">
                    <div class="spinner"></div>
                    <p>🧠 Analyzing your mood with AI...</p>
                    <p>🔍 Searching through 500+ meals using vector similarity...</p>
                    <p>🤖 Generating personalized explanation...</p>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(3)  # Simulate processing time
            
            # Simulate mood detection
            mood_keywords = {
                'stress': ['Stressed', 'Overwhelmed'],
                'tired': ['Tired', 'Exhausted'],
                'anxious': ['Anxious', 'Worried'],
                'sad': ['Sad', 'Down'],
                'happy': ['Happy', 'Joyful'],
                'angry': ['Irritable', 'Frustrated'],
                'lonely': ['Lonely', 'Isolated'],
                'excited': ['Excited', 'Energized']
            }
            
            detected_moods = ['Calm', 'Neutral']  # Default
            for keyword, moods in mood_keywords.items():
                if keyword in user_mood.lower():
                    detected_moods = moods
                    break
            
            # Select appropriate meal
            meals = load_demo_meals()
            selected_meal = None
            for meal in meals:
                if meal['mood_1'] in detected_moods or meal['mood_2'] in detected_moods:
                    selected_meal = meal
                    break
            
            if not selected_meal:
                selected_meal = random.choice(meals)
            
            # Display recommendation
            mood_emojis = {
                'Stressed': '😰', 'Overwhelmed': '🤯', 'Tired': '😴', 'Exhausted': '🥱',
                'Anxious': '😟', 'Worried': '😰', 'Sad': '😢', 'Down': '😔',
                'Happy': '😊', 'Joyful': '😄', 'Irritable': '😠', 'Frustrated': '😤',
                'Lonely': '😞', 'Isolated': '🙁', 'Excited': '🤩', 'Energized': '⚡',
                'Calm': '😌', 'Neutral': '😐'
            }
            
            emoji1 = mood_emojis.get(detected_moods[0], '😊')
            emoji2 = mood_emojis.get(detected_moods[1], '😊')
            
            st.markdown(f"""
            <div class="recommendation">
                <div class="mood-emoji">{emoji1}{emoji2}</div>
                <div class="meal-name">🍽️ {selected_meal['meal_name']}</div>
                
                <div class="meal-details">
                    <strong>🎭 Detected Moods:</strong> {detected_moods[0]} & {detected_moods[1]}
                </div>
                
                <div class="meal-details">
                    <strong>🎯 Why this meal:</strong> {selected_meal['reason']}
                </div>
                
                <div class="meal-details">
                    <strong>💪 Health Benefits:</strong> {selected_meal['benefit']}
                </div>
                
                <div class="meal-details">
                    <strong>🔥 Calories:</strong> {selected_meal['calories']} kcal | 
                    <strong>🌍 Cuisine:</strong> {selected_meal['cultural_theme']} | 
                    <strong>🥗 Type:</strong> {selected_meal['dietary_theme']}
                </div>
                
                <div class="meal-details">
                    <strong>🤖 AI Explanation:</strong> Based on your emotional state of feeling {detected_moods[0].lower()} and {detected_moods[1].lower()}, this meal provides the perfect combination of nutrients and comfort to help restore your emotional balance. The ingredients work synergistically to support your mood and energy levels.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Rating system
            st.markdown("### ⭐ Rate this recommendation:")
            rating = st.slider("How helpful was this suggestion?", 1, 5, 4)
            
            if st.button("📝 Submit Rating"):
                st.success(f"Thank you! You rated this {rating}/5 stars. The AI will learn from your feedback! 🙏")
        else:
            st.warning("📝 Please describe how you're feeling first!")

with col2:
    # Quick demo features
    st.markdown("""
    <div class="demo-card">
        <h4>🚀 Key Features</h4>
    </div>
    """, unsafe_allow_html=True)
    
    features = [
        "🎯 **Vector Search**: FAISS similarity matching",
        "🤖 **Small LLM**: DistilGPT-2 explanations", 
        "🔊 **Voice Analysis**: Audio mood detection",
        "📊 **Sentence Transformers**: Semantic embeddings",
        "💾 **Learning**: Adapts to your preferences",
        "⏰ **Smart Reminders**: Meal timing alerts",
        "🌍 **Cultural Diversity**: 8+ cuisine types",
        "🥗 **Dietary Options**: Vegan, Gluten-free, etc."
    ]
    
    for feature in features:
        st.markdown(feature)
    
    # Quick mood selector demo
    st.markdown("---")
    st.markdown("### 🎯 Quick Mood Demo")
    
    mood_options = {
        "😢 Feeling Down": ["Sad", "Lonely"],
        "😰 Stressed Out": ["Stressed", "Anxious"], 
        "😴 Tired & Drained": ["Tired", "Sluggish"],
        "😊 Happy & Content": ["Happy", "Grateful"],
        "🤩 Excited & Energized": ["Excited", "Motivated"]
    }
    
    selected_mood = st.selectbox("Choose your mood:", list(mood_options.keys()))
    
    if st.button("Get Quick Suggestion", use_container_width=True):
        moods = mood_options[selected_mood]
        meals = load_demo_meals()
        
        # Find matching meal
        matching_meal = None
        for meal in meals:
            if meal['mood_1'] in moods or meal['mood_2'] in moods:
                matching_meal = meal
                break
        
        if not matching_meal:
            matching_meal = random.choice(meals)
        
        st.success(f"🍽️ **{matching_meal['meal_name']}**")
        st.info(f"💡 {matching_meal['reason']}")
        st.markdown(f"**Benefits:** {matching_meal['benefit']}")

# Technology showcase
st.markdown("---")
st.markdown("## 🔬 Technology Behind the Magic")

tech_col1, tech_col2, tech_col3 = st.columns(3)

with tech_col1:
    st.markdown("""
    <div class="demo-card">
        <h4>🧠 AI Models</h4>
        <ul>
            <li><strong>Sentence Transformers</strong><br>all-MiniLM-L6-v2 (22MB)</li>
            <li><strong>Language Model</strong><br>DistilGPT-2 (82MB)</li>
            <li><strong>Emotion Classifier</strong><br>RoBERTa-based (250MB)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with tech_col2:
    st.markdown("""
    <div class="demo-card">
        <h4>🔍 Vector Search</h4>
        <ul>
            <li><strong>FAISS Index</strong><br>384-dimensional vectors</li>
            <li><strong>Similarity Search</strong><br>Cosine similarity matching</li>
            <li><strong>Real-time</strong><br>Sub-second responses</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with tech_col3:
    st.markdown("""
    <div class="demo-card">
        <h4>🎵 Audio Processing</h4>
        <ul>
            <li><strong>Speech-to-Text</strong><br>Whisper integration</li>
            <li><strong>Voice Emotion</strong><br>Librosa analysis</li>
            <li><strong>Text-to-Speech</strong><br>gTTS responses</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Sample data visualization
st.markdown("---")
st.markdown("## 📊 Sample Analytics")

# Create sample mood data
sample_data = {
    'Mood': ['Stressed', 'Tired', 'Anxious', 'Happy', 'Sad', 'Excited', 'Calm', 'Lonely'],
    'Frequency': [25, 20, 18, 15, 12, 8, 7, 5],
    'Recommended_Meals': [45, 38, 32, 28, 22, 15, 12, 8]
}

df = pd.DataFrame(sample_data)

col1, col2 = st.columns(2)

with col1:
    fig1 = px.pie(df, values='Frequency', names='Mood', 
                  title='Most Common Moods Detected',
                  color_discrete_sequence=px.colors.qualitative.Set3)
    fig1.update_layout(height=400)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.bar(df, x='Mood', y='Recommended_Meals',
                  title='Meals Recommended by Mood',
                  color='Recommended_Meals',
                  color_continuous_scale='viridis')
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)

# Call to action
st.markdown("---")
st.markdown("""
<div class="hero-section">
    <h2>🚀 Ready to Transform Your Meals?</h2>
    <p>Experience the future of personalized nutrition with AI-powered mood detection</p>
    <div style="margin-top: 2rem;">
        <strong>✨ What makes us different:</strong><br>
        🧠 Advanced AI with vector search & transformers<br>
        🎯 Personalized recommendations that learn from you<br>
        🔊 Multi-modal input (text, voice, audio)<br>
        🌍 500+ culturally diverse, mood-mapped meals<br>
        ⚡ Real-time processing with sub-second responses
    </div>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #666;">
    <p><strong>🧠 AI Mood Meal Assistant</strong> - Built with ❤️ using cutting-edge AI</p>
    <p>Powered by FAISS • Sentence Transformers • Small Language Models • Vector Search</p>
    <p><em>Transform your mood into the perfect meal with AI-powered recommendations!</em></p>
</div>
""", unsafe_allow_html=True)
