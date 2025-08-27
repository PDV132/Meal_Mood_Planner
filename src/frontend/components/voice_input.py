import streamlit as st
import requests
from voice_mood_detector import VoiceMoodDetector

def detect_mood_from_voice():
    st.markdown('<div class="voice-input-box">', unsafe_allow_html=True)
    st.subheader("🎤 Voice Mood Detection")
    
    detector = VoiceMoodDetector()
    
    if st.button("Start Voice Recording"):
        with st.spinner("Recording... Please speak about your day or current feelings..."):
            detected_mood = detector.process_voice_input()
            
        if detected_mood:
            st.success(f"Detected mood from voice: {detected_mood.title()}")
            return detected_mood
        else:
            st.error("Could not detect mood from voice. Please try again.")
            return None
            
    st.markdown('</div>', unsafe_allow_html=True)
    return None

def get_meal_suggestions(mood):
    """Get meal suggestions based on detected mood"""
    try:
        response = requests.post(
            "http://localhost:8000/api/suggest/meals",
            json={"mood": mood},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error getting meal suggestions: {str(e)}")
        return None
