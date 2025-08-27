import sounddevice as sd
import numpy as np
import librosa
import scipy.io.wavfile as wav
import os
from datetime import datetime

class VoiceMoodDetector:
    def __init__(self):
        self.sample_rate = 44100
        self.duration = 5  # Record for 5 seconds
        
    def record_voice(self):
        """Record voice input from microphone"""
        print("Recording... Speak now!")
        recording = sd.rec(int(self.duration * self.sample_rate),
                         samplerate=self.sample_rate,
                         channels=1,
                         dtype='float32')
        sd.wait()
        print("Recording complete!")
        return recording

    def extract_features(self, audio_data):
        """Extract audio features for mood detection"""
        # Convert to mono if needed
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)
        
        # Extract features
        mfcc = librosa.feature.mfcc(y=audio_data.flatten(), sr=self.sample_rate, n_mfcc=13)
        spectral_centroids = librosa.feature.spectral_centroid(y=audio_data.flatten(), sr=self.sample_rate)
        zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data.flatten())
        
        # Calculate energy and other features
        energy = np.sum(np.abs(audio_data)**2) / len(audio_data)
        pitch = librosa.yin(audio_data.flatten(), fmin=50, fmax=500, sr=self.sample_rate)
        
        # Combine features
        features = {
            'mfcc_mean': np.mean(mfcc),
            'spectral_centroid_mean': np.mean(spectral_centroids),
            'zero_crossing_rate_mean': np.mean(zero_crossing_rate),
            'energy': energy,
            'pitch_mean': np.mean(pitch)
        }
        
        return features

    def detect_mood(self, features):
        """Detect mood based on audio features"""
        # Simple rule-based mood detection
        # You can replace this with a more sophisticated ML model
        if features['energy'] > 0.1 and features['pitch_mean'] > 200:
            return "excited"
        elif features['energy'] > 0.05 and features['pitch_mean'] > 150:
            return "happy"
        elif features['energy'] < 0.03 and features['pitch_mean'] < 150:
            return "sad"
        elif features['energy'] < 0.05 and features['spectral_centroid_mean'] < 1000:
            return "tired"
        else:
            return "neutral"

    def save_recording(self, recording):
        """Save recording to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"voice_recording_{timestamp}.wav"
        wav.write(filename, self.sample_rate, recording)
        return filename

    def process_voice_input(self):
        """Main function to process voice input and detect mood"""
        try:
            # Record voice
            recording = self.record_voice()
            
            # Extract features
            features = self.extract_features(recording)
            
            # Detect mood
            mood = self.detect_mood(features)
            
            # Save recording (optional)
            # filename = self.save_recording(recording)
            
            return mood
            
        except Exception as e:
            print(f"Error processing voice input: {str(e)}")
            return None
