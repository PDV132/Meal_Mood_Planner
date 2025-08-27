from transformers import pipeline
import soundfile as sf
import numpy as np

# Initialize the speech recognition pipeline
asr_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")

def transcribe_audio(audio_path: str) -> str:
    """
    Transcribes audio file to text using Whisper model
    
    Args:
        audio_path (str): Path to the audio file
        
    Returns:
        str: Transcribed text
    """
    try:
        # Load audio file
        audio, sample_rate = sf.read(audio_path)
        
        # Convert to mono if stereo
        if len(audio.shape) > 1:
            audio = audio.mean(axis=1)
        
        # Normalize audio
        audio = audio / np.max(np.abs(audio))
        
        # Transcribe
        result = asr_pipeline({"raw": audio, "sampling_rate": sample_rate})
        
        return result["text"]
        
    except Exception as e:
        print(f"Error in transcription: {str(e)}")
        return "Could not process the audio file."
