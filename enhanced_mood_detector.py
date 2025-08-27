import numpy as np
import librosa
from transformers import pipeline, Wav2Vec2Processor, Wav2Vec2ForSequenceClassification
import torch
import pickle
import os
from datetime import datetime
from typing import Tuple, Dict, List

class EnhancedMoodDetector:
    def __init__(self):
        # Load emotion detection models
        self.text_classifier = pipeline(
            "text-classification", 
            model="j-hartmann/emotion-english-distilroberta-base", 
            return_all_scores=True
        )
        
        # Load audio emotion detection model
        try:
            self.audio_processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base")
            self.audio_model = Wav2Vec2ForSequenceClassification.from_pretrained(
                "facebook/wav2vec2-base", 
                num_labels=7  # 7 basic emotions
            )
        except:
            print("Audio emotion model not available, using text-only detection")
            self.audio_processor = None
            self.audio_model = None
        
        # Emotion mapping for consistency
        self.emotion_mapping = {
            'joy': 'Happy',
            'sadness': 'Sad', 
            'anger': 'Irritable',
            'fear': 'Anxious',
            'surprise': 'Surprised',
            'disgust': 'Grumpy',
            'neutral': 'Calm',
            'happy': 'Happy',
            'sad': 'Sad',
            'angry': 'Irritable',
            'fearful': 'Anxious',
            'surprised': 'Surprised',
            'disgusted': 'Grumpy',
            'calm': 'Calm'
        }
        
        # Load user preferences
        self.preferences_file = "user_preferences.pkl"
        self.user_preferences = self.load_preferences()
    
    def extract_audio_features(self, audio_path: str) -> np.ndarray:
        """Extract audio features for emotion detection"""
        try:
            # Load audio file
            audio, sr = librosa.load(audio_path, sr=16000)
            
            # Extract features
            features = {}
            
            # Spectral features
            features['mfcc'] = np.mean(librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13), axis=1)
            features['spectral_centroid'] = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr))
            features['spectral_rolloff'] = np.mean(librosa.feature.spectral_rolloff(y=audio, sr=sr))
            features['zero_crossing_rate'] = np.mean(librosa.feature.zero_crossing_rate(audio))
            
            # Pitch and energy
            pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
            features['pitch_mean'] = np.mean(pitches[pitches > 0]) if len(pitches[pitches > 0]) > 0 else 0
            features['energy'] = np.mean(librosa.feature.rms(y=audio))
            
            # Tempo
            tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
            features['tempo'] = tempo
            
            return np.concatenate([
                features['mfcc'],
                [features['spectral_centroid'], features['spectral_rolloff'], 
                 features['zero_crossing_rate'], features['pitch_mean'], 
                 features['energy'], features['tempo']]
            ])
            
        except Exception as e:
            print(f"Error extracting audio features: {e}")
            return np.zeros(20)  # Return zero features if extraction fails
    
    def detect_mood_from_audio_features(self, features: np.ndarray) -> Tuple[str, str]:
        """Detect mood from audio features using rule-based approach"""
        try:
            # Simple rule-based emotion detection based on audio features
            energy = features[-3] if len(features) > 3 else 0
            pitch_mean = features[-4] if len(features) > 4 else 0
            tempo = features[-1] if len(features) > 1 else 0
            zcr = features[-5] if len(features) > 5 else 0
            
            # Normalize features
            energy_norm = min(energy * 1000, 1.0)  # Normalize energy
            pitch_norm = min(pitch_mean / 200, 1.0) if pitch_mean > 0 else 0
            tempo_norm = min(tempo / 200, 1.0) if tempo > 0 else 0
            zcr_norm = min(zcr * 10, 1.0)
            
            # Rule-based classification
            if energy_norm > 0.7 and tempo_norm > 0.6:
                primary = "Energized"
                secondary = "Happy" if pitch_norm > 0.5 else "Restless"
            elif energy_norm < 0.3 and tempo_norm < 0.4:
                primary = "Tired"
                secondary = "Sad" if pitch_norm < 0.3 else "Sluggish"
            elif zcr_norm > 0.6 and energy_norm > 0.5:
                primary = "Anxious"
                secondary = "Restless" if tempo_norm > 0.5 else "Nervous"
            elif pitch_norm > 0.7:
                primary = "Excited"
                secondary = "Happy" if energy_norm > 0.5 else "Curious"
            elif pitch_norm < 0.2:
                primary = "Gloomy"
                secondary = "Sad" if energy_norm < 0.4 else "Grumpy"
            else:
                primary = "Calm"
                secondary = "Peaceful" if energy_norm < 0.5 else "Content"
            
            return primary, secondary
            
        except Exception as e:
            print(f"Error in audio mood detection: {e}")
            return "Calm", "Neutral"
    
    def detect_mood_from_text(self, text: str) -> Tuple[str, str]:
        """Enhanced text-based mood detection"""
        try:
            results = self.text_classifier(text)[0]
            sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
            
            # Map emotions to our mood categories
            primary = self.emotion_mapping.get(sorted_results[0]['label'].lower(), sorted_results[0]['label'])
            secondary = self.emotion_mapping.get(sorted_results[1]['label'].lower(), sorted_results[1]['label'])
            
            return primary, secondary
            
        except Exception as e:
            print(f"Error in text mood detection: {e}")
            return "Calm", "Neutral"
    
    def detect_mood_from_audio(self, audio_path: str, transcribed_text: str = None) -> Tuple[str, str]:
        """Combined audio and text mood detection"""
        try:
            # Extract audio features
            audio_features = self.extract_audio_features(audio_path)
            audio_mood1, audio_mood2 = self.detect_mood_from_audio_features(audio_features)
            
            # If we have transcribed text, combine with text analysis
            if transcribed_text and len(transcribed_text.strip()) > 0:
                text_mood1, text_mood2 = self.detect_mood_from_text(transcribed_text)
                
                # Combine audio and text moods (prioritize text for primary, audio for secondary)
                return text_mood1, audio_mood2
            
            return audio_mood1, audio_mood2
            
        except Exception as e:
            print(f"Error in combined mood detection: {e}")
            return "Calm", "Neutral"
    
    def load_preferences(self) -> Dict:
        """Load user preferences from file"""
        try:
            if os.path.exists(self.preferences_file):
                with open(self.preferences_file, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            print(f"Error loading preferences: {e}")
        
        return {}
    
    def save_preferences(self):
        """Save user preferences to file"""
        try:
            with open(self.preferences_file, 'wb') as f:
                pickle.dump(self.user_preferences, f)
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
    def update_user_preference(self, user_id: str, mood_combo: Tuple[str, str], 
                             meal_name: str, rating: int):
        """Update user preferences based on meal rating"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                'meal_ratings': {},
                'mood_preferences': {},
                'dietary_restrictions': [],
                'cultural_preferences': [],
                'last_updated': datetime.now().isoformat()
            }
        
        # Store meal rating
        mood_key = f"{mood_combo[0]}_{mood_combo[1]}"
        if mood_key not in self.user_preferences[user_id]['meal_ratings']:
            self.user_preferences[user_id]['meal_ratings'][mood_key] = {}
        
        self.user_preferences[user_id]['meal_ratings'][mood_key][meal_name] = {
            'rating': rating,
            'timestamp': datetime.now().isoformat()
        }
        
        # Update mood preferences
        if mood_key not in self.user_preferences[user_id]['mood_preferences']:
            self.user_preferences[user_id]['mood_preferences'][mood_key] = []
        
        if rating >= 4:  # Good rating
            if meal_name not in self.user_preferences[user_id]['mood_preferences'][mood_key]:
                self.user_preferences[user_id]['mood_preferences'][mood_key].append(meal_name)
        
        self.user_preferences[user_id]['last_updated'] = datetime.now().isoformat()
        self.save_preferences()
    
    def get_user_preferences(self, user_id: str) -> Dict:
        """Get user preferences"""
        return self.user_preferences.get(user_id, {})
    
    def set_dietary_restrictions(self, user_id: str, restrictions: List[str]):
        """Set dietary restrictions for user"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                'meal_ratings': {},
                'mood_preferences': {},
                'dietary_restrictions': [],
                'cultural_preferences': [],
                'last_updated': datetime.now().isoformat()
            }
        
        self.user_preferences[user_id]['dietary_restrictions'] = restrictions
        self.user_preferences[user_id]['last_updated'] = datetime.now().isoformat()
        self.save_preferences()
    
    def set_cultural_preferences(self, user_id: str, preferences: List[str]):
        """Set cultural food preferences for user"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                'meal_ratings': {},
                'mood_preferences': {},
                'dietary_restrictions': [],
                'cultural_preferences': [],
                'last_updated': datetime.now().isoformat()
            }
        
        self.user_preferences[user_id]['cultural_preferences'] = preferences
        self.user_preferences[user_id]['last_updated'] = datetime.now().isoformat()
        self.save_preferences()
