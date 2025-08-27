import streamlit as st
import requests
import base64
import json
import time
from datetime import datetime, timedelta
from components.preferences import save_dietary_preferences
from components.voice_input import detect_mood_from_voice, get_meal_suggestions

# Guard clause for pandas import
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# Guard clause for plotly import
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Configure page
st.set_page_config(
    page_title="🧠 AI Mood Meal Assistant",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* Main app styling */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Custom font */
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 0;
    }
    
    /* Card styling */
    .mood-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        border: 1px solid #f0f0f0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .mood-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
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
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("🧠 AI Mood Meal Assistant")
    st.markdown("Let's find the perfect meal based on your mood!")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add tabs for different functions
    tab1, tab2 = st.tabs(["Voice Mood Detection", "Preferences"])
    
    with tab1:
        st.markdown('<div class="mood-card">', unsafe_allow_html=True)
        st.write("Speak about your day or current feelings, and I'll suggest meals based on your mood!")
        detected_mood = detect_mood_from_voice()
        
        if detected_mood:
            suggestions = get_meal_suggestions(detected_mood)
            
            if suggestions:
                st.subheader("🍳 Suggested Meals")
                for suggestion in suggestions:
                    st.write(f"• {suggestion['name']}")
                    st.write(f"  *Why this meal:* {suggestion['reason']}")
                    st.write("---")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        save_dietary_preferences()

if __name__ == "__main__":
    main()

st.markdown("""
<style>
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* Input styling */
    .stTextArea > div > div > textarea {
        border-radius: 15px;
        border: 2px solid #e0e0e0;
        padding: 1rem;
        font-size: 1rem;
        transition: border-color 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Success message styling */
    .meal-suggestion {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(79, 172, 254, 0.3);
    }
    
    .meal-suggestion h3 {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    .meal-info {
        background: rgba(255,255,255,0.1);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        backdrop-filter: blur(10px);
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        text-align: center;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    
    /* Notification styling */
    .notification {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        color: #8b0000;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #ff6b6b;
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Mood emoji styling */
    .mood-emoji {
        font-size: 3rem;
        text-align: center;
        margin: 1rem 0;
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state with guardrails
def initialize_session_state():
    """Initialize session state with proper validation and defaults"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = f"user_{int(time.time())}"
    if 'meal_history' not in st.session_state:
        st.session_state.meal_history = []
    if 'mood_history' not in st.session_state:
        st.session_state.mood_history = []
    if 'preferences_set' not in st.session_state:
        st.session_state.preferences_set = False
    if 'api_errors' not in st.session_state:
        st.session_state.api_errors = 0
    if 'last_request_time' not in st.session_state:
        st.session_state.last_request_time = 0

# Input validation functions
def validate_text_input(text):
    """Validate user text input with security checks"""
    if not text or not isinstance(text, str):
        return False, "Please provide valid text input"
    
    # Length validation
    if len(text.strip()) < 5:
        return False, "Please provide a more detailed description (at least 5 characters)"
    
    if len(text) > 1000:
        return False, "Input too long. Please keep it under 1000 characters"
    
    # Basic security checks - prevent potential injection
    dangerous_patterns = ['<script', 'javascript:', 'eval(', 'exec(']
    text_lower = text.lower()
    for pattern in dangerous_patterns:
        if pattern in text_lower:
            return False, "Invalid input detected"
    
    return True, "Valid input"

def validate_audio_file(uploaded_file):
    """Validate uploaded audio file"""
    if not uploaded_file:
        return False, "No file uploaded"
    
    # File size check (max 10MB)
    if uploaded_file.size > 10 * 1024 * 1024:
        return False, "File too large. Please upload files smaller than 10MB"
    
    # File type validation
    allowed_types = ['audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/m4a']
    if uploaded_file.type not in allowed_types:
        return False, "Invalid file type. Please upload WAV, MP3, or M4A files only"
    
    return True, "Valid audio file"

def rate_limit_check():
    """Simple rate limiting to prevent API abuse"""
    current_time = time.time()
    if current_time - st.session_state.last_request_time < 2:  # 2 second cooldown
        return False, "Please wait a moment before making another request"
    
    st.session_state.last_request_time = current_time
    return True, "Rate limit OK"

def safe_api_request(url, method='POST', **kwargs):
    """Make API requests with proper error handling and timeout"""
    try:
        # Rate limiting
        rate_ok, rate_msg = rate_limit_check()
        if not rate_ok:
            return None, rate_msg
        
        # Set timeout and make request
        kwargs['timeout'] = 30  # 30 second timeout
        
        if method == 'POST':
            response = requests.post(url, **kwargs)
        else:
            response = requests.get(url, **kwargs)
        
        # Reset error counter on success
        if response.status_code == 200:
            st.session_state.api_errors = 0
            return response, "Success"
        else:
            st.session_state.api_errors += 1
            return None, f"Server error: {response.status_code}"
            
    except requests.exceptions.Timeout:
        st.session_state.api_errors += 1
        return None, "Request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        st.session_state.api_errors += 1
        return None, "Could not connect to server. Please check if the backend is running."
    except Exception as e:
        st.session_state.api_errors += 1
        return None, f"Unexpected error: {str(e)}"

# Initialize session state
initialize_session_state()

# Header
st.markdown("""
<div class="main-header">
    <h1>🧠 AI Mood Meal Assistant</h1>
    <p>Discover the perfect meal for your emotional state with AI-powered recommendations</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for user preferences and history
with st.sidebar:
    st.markdown("### 👤 Your Profile")
    
    # User preferences
    with st.expander("🎯 Set Your Preferences", expanded=not st.session_state.preferences_set):
        st.markdown("**Dietary Restrictions:**")
        dietary_restrictions = st.multiselect(
            "Select any dietary restrictions:",
            ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Nut-Free", "Low-Carb", "Keto", "Paleo"],
            key="dietary_restrictions"
        )
        
        st.markdown("**Cultural Preferences:**")
        cultural_preferences = st.multiselect(
            "Preferred cuisines:",
            ["South Asian", "East Asian", "Mediterranean", "Middle Eastern", "Latin American", 
             "African", "Western Comfort", "Fusion"],
            key="cultural_preferences"
        )
        
        if st.button("💾 Save Preferences"):
            # Save preferences via API
            try:
                requests.post("http://localhost:8000/set-preferences", json={
                    "user_id": st.session_state.user_id,
                    "dietary_restrictions": dietary_restrictions,
                    "cultural_preferences": cultural_preferences
                })
                st.session_state.preferences_set = True
                st.success("✅ Preferences saved!")
            except:
                st.warning("⚠️ Could not save preferences. Server may be offline.")
    
    # Mood history visualization with guardrails
    if st.session_state.mood_history:
        st.markdown("### 📊 Your Mood Trends")
        
        try:
            if PANDAS_AVAILABLE:
                # Create mood frequency chart with error handling
                mood_df = pd.DataFrame(st.session_state.mood_history)
                if not mood_df.empty and len(mood_df) > 0:
                    mood_counts = mood_df['primary_mood'].value_counts()
                    
                    if PLOTLY_AVAILABLE and len(mood_counts) > 0:
                        fig = px.pie(
                            values=mood_counts.values,
                            names=mood_counts.index,
                            title="Your Most Common Moods",
                            color_discrete_sequence=px.colors.qualitative.Set3
                        )
                        fig.update_layout(height=300, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        # Fallback text display
                        st.markdown("**Your most common moods:**")
                        for mood, count in mood_counts.head(5).items():
                            st.markdown(f"• {mood}: {count} times")
            else:   
                # Manual mood counting without pandas
                mood_counts = {}
                for entry in st.session_state.mood_history:
                    mood = entry.get('primary_mood', 'Unknown')
                    mood_counts[mood] = mood_counts.get(mood, 0) + 1
                
                # Sort by count and display top 5
                sorted_moods = sorted(mood_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                st.markdown("**Your most common moods:**")
                for mood, count in sorted_moods:
                    st.markdown(f"• {mood}: {count} times")
                    
        except Exception as e:
            st.error(f"Error displaying mood trends: {str(e)}")
    
    # Recent meals
    if st.session_state.meal_history:
        st.markdown("### 🍽️ Recent Meals")
        for meal in st.session_state.meal_history[-3:]:
            st.markdown(f"""
            <div class="metric-card">
                <strong>{meal['name']}</strong><br>
                <small>{meal['timestamp']}</small>
            </div>
            """, unsafe_allow_html=True)


# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Text input section
    st.markdown("""
    <div class="mood-card">
        <h3>💭 Tell me how you're feeling</h3>
        <p>Describe your current mood and emotions in your own words</p>
    </div>
    """, unsafe_allow_html=True)
    
    user_input = st.text_area(
        "Describe your mood",
        height=120,
        placeholder="I'm feeling tired and a bit anxious about work tomorrow...",
        help="Be as descriptive as possible about your current emotional state",
        label_visibility="hidden"
    )
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    
    with col_btn2:
        analyze_text_btn = st.button("🔍 Analyze My Mood", use_container_width=True)
    
    if analyze_text_btn:
        # Input validation with guardrails
        is_valid, validation_msg = validate_text_input(user_input)
        
        if not is_valid:
            st.error(f"❌ {validation_msg}")
        elif st.session_state.api_errors >= 5:
            st.error("🚫 Too many failed requests. Please refresh the page and try again.")
        else:
            with st.spinner("🧠 Analyzing your mood and finding the perfect meal..."):
                # Use safe API request with guardrails
                response, error_msg = safe_api_request(
                    "http://localhost:8000/suggest-meal-from-text",
                    json={"text": user_input.strip(), "user_id": st.session_state.user_id}
                )
                
                if response and response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Validate response data
                        if not all(key in data for key in ['meal', 'mood_detected', 'reason', 'benefit']):
                            st.error("❌ Invalid response from server")
                        else:
                            # Display meal suggestion with beautiful styling
                            meal_name = str(data.get('meal', 'Unknown Meal'))[:100]  # Limit length
                            moods = data.get('mood_detected', ['Unknown', 'Unknown'])
                            reason = str(data.get('reason', 'No reason provided'))[:500]
                            benefit = str(data.get('benefit', 'No benefits listed'))[:500]
                            
                            st.markdown(f""" 
                            <div class="meal-suggestion">
                                <div class="mood-emoji">🍽️</div>
                                <h3>Recommended: {meal_name}</h3>
                                
                                <div class="meal-info">
                                    <strong>🎭 Detected Moods:</strong> {moods[0]} & {moods[1]}
                                </div>
                                
                                <div class="meal-info">
                                    <strong>🎯 Why this meal:</strong> {reason}
                                </div>
                                
                                <div class="meal-info">
                                    <strong>💪 Health Benefits:</strong> {benefit}
                                </div>
                                
                                <div class="meal-info">
                                    <strong>🔥 Calories:</strong> {data.get('calories', 'N/A')} kcal
                                </div>
                                
                                <div class="meal-info">
                                    <strong>🌍 Cuisine:</strong> {data.get('cultural_theme', 'Mixed')}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # AI explanation with length limit
                            if 'explanation' in data and data['explanation']:
                                explanation = str(data['explanation'])[:1000]  # Limit length
                                st.markdown("### 🤖 AI Nutritionist Says:")
                                st.info(explanation)
                            
                            # Rating system
                            st.markdown("### ⭐ Rate this suggestion:")
                            rating = st.slider("How helpful was this recommendation?", 1, 5, 3)
                            
                            if st.button("📝 Submit Rating"):
                                rating_response, rating_error = safe_api_request(
                                    "http://localhost:8000/rate-meal",
                                    json={
                                        "user_id": st.session_state.user_id,
                                        "mood_combo": moods,
                                        "meal_name": meal_name,
                                        "rating": int(rating)
                                    }
                                )
                                
                                if rating_response:
                                    st.success("Thank you for your feedback! 🙏")
                                else:
                                    st.warning(f"Could not save rating: {rating_error}")
                            
                            # Update session state with validation
                            try:
                                st.session_state.mood_history.append({
                                    'primary_mood': str(moods[0])[:50],
                                    'secondary_mood': str(moods[1])[:50],
                                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                                })
                                
                                st.session_state.meal_history.append({
                                    'name': meal_name,
                                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                                })
                                
                                # Limit history size to prevent memory issues
                                if len(st.session_state.mood_history) > 100:
                                    st.session_state.mood_history = st.session_state.mood_history[-50:]
                                if len(st.session_state.meal_history) > 100:
                                    st.session_state.meal_history = st.session_state.meal_history[-50:]
                                    
                            except Exception as e:
                                st.warning("Could not save to history")
                    
                    except json.JSONDecodeError:
                        st.error("❌ Invalid response format from server")
                    except Exception as e:
                        st.error(f"❌ Error processing response: {str(e)[:100]}")
                        
                else:
                    st.error(f"😔 {error_msg}")

with col2:
    # Quick mood selector
    st.markdown("""
    <div class="mood-card">
        <h4>🚀 Quick Mood Selection</h4>
        <p>Or choose from common moods</p>
    </div>
    """, unsafe_allow_html=True)
    
    mood_categories = {
        "😢 Negative": ["Sad", "Anxious", "Tired", "Stressed", "Lonely", "Frustrated"],
        "😊 Positive": ["Happy", "Excited", "Energized", "Confident", "Grateful", "Peaceful"],
        "🤔 Neutral": ["Calm", "Bored", "Curious", "Reflective", "Focused", "Balanced"]
    }
    
    selected_category = st.selectbox("Choose mood category:", list(mood_categories.keys()))
    primary_mood = st.selectbox("Primary mood:", mood_categories[selected_category])
    secondary_mood = st.selectbox("Secondary mood:", mood_categories[selected_category])
    
    if st.button("🎯 Get Quick Suggestion", use_container_width=True):
        if st.session_state.api_errors >= 5:
            st.error("🚫 Too many failed requests. Please refresh the page and try again.")
        else:
            with st.spinner("Finding your perfect meal..."):
                # Use safe API request with guardrails
                response, error_msg = safe_api_request(
                    "http://localhost:8000/suggest-meal-from-moods",
                    json={
                        "mood1": str(primary_mood)[:50],  # Limit length
                        "mood2": str(secondary_mood)[:50],
                        "user_id": st.session_state.user_id
                    }
                )
                
                if response and response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Validate response data
                        if not all(key in data for key in ['meal', 'reason', 'benefit']):
                            st.error("❌ Invalid response from server")
                        else:
                            # Sanitize response data
                            meal_name = str(data.get('meal', 'Unknown Meal'))[:100]
                            reason = str(data.get('reason', 'No reason provided'))[:300]
                            benefit = str(data.get('benefit', 'No benefits listed'))[:300]
                            
                            st.success(f"🍽️ **{meal_name}**")
                            st.info(f"💡 {reason}")
                            st.markdown(f"**Benefits:** {benefit}")
                            
                            # Update session state for quick suggestions too
                            try:
                                st.session_state.mood_history.append({
                                    'primary_mood': str(primary_mood)[:50],
                                    'secondary_mood': str(secondary_mood)[:50],
                                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                                })
                                
                                st.session_state.meal_history.append({
                                    'name': meal_name,
                                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                                })
                            except Exception:
                                pass  # Silent fail for history updates
                    
                    except json.JSONDecodeError:
                        st.error("❌ Invalid response format from server")
                    except Exception as e:
                        st.error(f"❌ Error processing response: {str(e)[:100]}")
                        
                else:
                    st.error(f"😔 {error_msg}")

# Audio input section with guardrails
st.markdown("---")
st.markdown("### 🎙️ Voice Input (Upload Audio)")

uploaded_audio = st.file_uploader("Upload an audio file describing your mood", type=['wav', 'mp3', 'm4a'])

if uploaded_audio is not None:
    # Validate audio file with guardrails
    is_valid_audio, audio_msg = validate_audio_file(uploaded_audio)
    
    if not is_valid_audio:
        st.error(f"❌ {audio_msg}")
    else:
        st.audio(uploaded_audio)
        st.success(f"✅ Audio file loaded successfully ({uploaded_audio.size / 1024 / 1024:.1f} MB)")
        
        if st.button("🎵 Analyze Audio Mood"):
            if st.session_state.api_errors >= 5:
                st.error("🚫 Too many failed requests. Please refresh the page and try again.")
            else:
                with st.spinner("🎵 Analyzing your voice and emotions..."):
                    # Use safe API request for audio
                    response, error_msg = safe_api_request(
                        "http://localhost:8000/suggest-meal-from-audio",
                        files={"audio": uploaded_audio},
                        data={"user_id": st.session_state.user_id}
                    )
                    
                    if response and response.status_code == 200:
                        try:
                            data = response.json()
                            
                            # Validate audio response data
                            if not all(key in data for key in ['meal', 'mood_detected', 'reason', 'benefit']):
                                st.error("❌ Invalid audio response from server")
                            else:
                                # Sanitize audio response data
                                meal_name = str(data.get('meal', 'Unknown Meal'))[:100]
                                moods = data.get('mood_detected', ['Unknown', 'Unknown'])
                                reason = str(data.get('reason', 'No reason provided'))[:500]
                                benefit = str(data.get('benefit', 'No benefits listed'))[:500]
                                
                                # Beautiful audio result display
                                st.markdown(f"""
                                <div class="meal-suggestion">
                                    <div class="mood-emoji">🎤</div>
                                    <h3>Voice Analysis Result: {meal_name}</h3>
                                    
                                    <div class="meal-info">
                                        <strong>🎭 Voice Emotions Detected:</strong> {moods[0]} & {moods[1]}
                                    </div>
                                    
                                    <div class="meal-info">
                                        <strong>🎯 Recommendation Reason:</strong> {reason}
                                    </div>
                                    
                                    <div class="meal-info">
                                        <strong>💪 Health Benefits:</strong> {benefit}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Play AI response if available (with validation)
                                if "explanation_audio" in data and data["explanation_audio"]:
                                    try:
                                        audio_b64 = str(data["explanation_audio"])
                                        # Basic validation of base64 audio
                                        if len(audio_b64) > 50 and audio_b64.replace('+', '').replace('/', '').replace('=', '').isalnum():
                                            audio_html = f"""
                                            <div style="text-align: center; margin: 2rem 0;">
                                                <h4>🔊 Listen to your personalized meal explanation:</h4>
                                                <audio controls style="width: 100%; max-width: 400px;">
                                                    <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
                                                </audio>
                                            </div>
                                            """
                                            st.markdown(audio_html, unsafe_allow_html=True)
                                    except Exception:
                                        st.warning("Could not load audio response")
                                
                                # Display explanation with length limit
                                explanation = str(data.get('explanation', ''))[:1000]
                                if explanation:
                                    st.markdown(f"**🤖 Detailed Explanation:** {explanation}")
                        
                        except json.JSONDecodeError:
                            st.error("❌ Invalid audio response format from server")
                        except Exception as e:
                            st.error(f"❌ Error processing audio response: {str(e)[:100]}")
                    
                    else:
                        st.error(f"😔 {error_msg}")



# Meal reminder system
st.markdown("---")
st.markdown("### ⏰ Smart Meal Reminders")

reminder_col1, reminder_col2 = st.columns(2)

with reminder_col1:
    st.markdown("#### 🔔 Reminder Settings")
    reminder_enabled = st.checkbox("Enable meal reminders", value=True)
    reminder_interval = st.slider("Reminder interval (hours)", 2, 8, 3)
    
    if st.button("💾 Save Reminder Settings"):
        st.success("✅ Reminder settings saved!")

with reminder_col2:
    # Check for missed meals
    if st.session_state.meal_history:
        last_meal_time = datetime.strptime(st.session_state.meal_history[-1]['timestamp'], "%Y-%m-%d %H:%M")
        time_since_last_meal = datetime.now() - last_meal_time
        
        if time_since_last_meal > timedelta(hours=3):
            st.markdown("""
            <div class="notification">
                <h4>🍽️ Meal Reminder</h4>
                <p>It's been over 3 hours since your last meal. Time to nourish your body and mood!</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🍽️ Get Meal Suggestion Now"):
                st.rerun()

# Footer with tips
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 15px; color: white; margin-top: 2rem;">
    <h4>💡 Pro Tips for Better Mood-Food Connection</h4>
    <div style="display: flex; justify-content: space-around; flex-wrap: wrap; margin-top: 1rem;">
        <div style="margin: 0.5rem; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 10px; backdrop-filter: blur(10px);">
            <strong>🧘 Mindful Eating</strong><br>
            <small>Pay attention to how foods make you feel</small>
        </div>
        <div style="margin: 0.5rem; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 10px; backdrop-filter: blur(10px);">
            <strong>⏰ Regular Meals</strong><br>
            <small>Consistent eating helps stabilize mood</small>
        </div>
        <div style="margin: 0.5rem; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 10px; backdrop-filter: blur(10px);">
            <strong>🌈 Variety</strong><br>
            <small>Different nutrients support different moods</small>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
