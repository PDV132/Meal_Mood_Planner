import streamlit as st
from speech_to_text import transcribe_audio
from enhanced_mood_detector import analyze_mood
from enhanced_meal_suggester import get_meal_recommendation

def detect_mood_from_voice():
    """Detect mood from voice input"""
    st.write("🎤 Click the button below and speak about your current mood")
    
    if st.button("Start Recording"):
        with st.spinner("Recording... Please speak about how you're feeling"):
            try:
                text = transcribe_audio()
                if text:
                    mood = analyze_mood(text)
                    return mood
                else:
                    st.error("❌ No speech detected. Please try again.")
            except Exception as e:
                st.error(f"❌ Error recording audio: {str(e)}")
    return None

def get_meal_suggestions(mood):
    """Get meal suggestions based on detected mood"""
    if not mood:
        return None
        
    try:
        suggestions = get_meal_recommendation(mood)
        return suggestions
    except Exception as e:
        st.error(f"❌ Error getting meal suggestions: {str(e)}")
        return None
