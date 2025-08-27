import streamlit as st
import time
import requests
from pathlib import Path
import tempfile
import os

def record_voice():
    """
    Records voice input and returns the audio file path
    """
    st.write("🎙️ Click below to start recording your mood description")
    
    # Create audio recorder
    audio = st.audio_recorder(
        text="Click to record",
        recording_color="#e8576e",
        neutral_color="#6aa36f"
    )

    if audio is not None:
        # Create a temporary file to save the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            # Write audio data to the temporary file
            tmp_file.write(audio.tobytes())
            tmp_path = tmp_file.name

        try:
            # Display success message
            st.success("Voice recorded successfully! Processing...")
            
            # Send the audio file to the backend
            files = {'audio': ('recording.wav', open(tmp_path, 'rb'), 'audio/wav')}
            response = requests.post(
                "http://localhost:8000/api/mood/analyze-voice",
                files=files
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('text', '')
            else:
                st.error("Error analyzing voice. Please try again.")
                return None
                
        except Exception as e:
            st.error(f"Error processing voice: {str(e)}")
            return None
        finally:
            # Clean up the temporary file
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    return None
