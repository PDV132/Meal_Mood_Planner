from transformers import pipeline
from pydub import AudioSegment

# Load HuggingFace Whisper model
pipe = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")

def transcribe_audio(audio_path: str):
    # Convert audio to a supported format if necessary
    try:
        audio = AudioSegment.from_file(audio_path)
        # Export to WAV as it's a widely supported format
        wav_path = "temp.wav"
        audio.export(wav_path, format="wav")
        result = pipe(wav_path)
        return result["text"]
    except Exception as e:
        print(f"Error processing audio file: {e}")
        return "Could not process the audio file."