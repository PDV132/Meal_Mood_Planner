from transformers import pipeline
import torch
from typing import Dict, List, Optional

class EnhancedMoodDetector:
    def __init__(self):
        # Initialize sentiment analysis pipeline
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=0 if torch.cuda.is_available() else -1
        )
        
        # Mood categories and their associated terms
        self.mood_categories = {
            "happy": ["happy", "joyful", "excited", "cheerful", "content"],
            "sad": ["sad", "down", "depressed", "gloomy", "unhappy"],
            "stressed": ["stressed", "anxious", "worried", "overwhelmed"],
            "energetic": ["energetic", "active", "lively", "vibrant"],
            "tired": ["tired", "exhausted", "fatigued", "sleepy"],
            "hungry": ["hungry", "starving", "famished"],
            "cozy": ["cozy", "comfortable", "relaxed", "peaceful"]
        }
        
    def detect_mood(
        self, 
        text: str,
        additional_context: Optional[Dict] = None
    ) -> Dict[str, float]:
        """
        Analyze text to detect mood with confidence scores
        Returns dict of mood categories and their confidence scores
        """
        # Get sentiment analysis
        sentiment = self.sentiment_analyzer(text)[0]
        
        # Initialize mood scores
        mood_scores = {mood: 0.0 for mood in self.mood_categories.keys()}
        
        # Basic sentiment mapping
        if sentiment["label"] == "POSITIVE":
            mood_scores["happy"] += sentiment["score"]
            mood_scores["energetic"] += sentiment["score"] * 0.5
        else:
            mood_scores["sad"] += sentiment["score"]
            mood_scores["tired"] += sentiment["score"] * 0.5
            
        # Word-based analysis
        text_lower = text.lower()
        for mood, terms in self.mood_categories.items():
            for term in terms:
                if term in text_lower:
                    mood_scores[mood] += 0.5
                    
        # Normalize scores
        total = sum(mood_scores.values()) or 1.0
        mood_scores = {
            k: v/total for k, v in mood_scores.items()
        }
        
        # Add context-based adjustments if provided
        if additional_context:
            self._adjust_for_context(mood_scores, additional_context)
            
        return mood_scores
        
    def _adjust_for_context(
        self,
        mood_scores: Dict[str, float],
        context: Dict
    ) -> None:
        """Adjust mood scores based on additional context"""
        # Time-based adjustments
        if "time" in context:
            hour = context["time"].hour
            if 22 <= hour or hour <= 5:
                mood_scores["tired"] *= 1.2
            elif 11 <= hour <= 13:
                mood_scores["hungry"] *= 1.2
                
        # Weather-based adjustments
        if "weather" in context:
            if context["weather"] == "rainy":
                mood_scores["cozy"] *= 1.2
            elif context["weather"] == "sunny":
                mood_scores["happy"] *= 1.1
                mood_scores["energetic"] *= 1.1
                
    def get_primary_mood(
        self, 
        text: str,
        additional_context: Optional[Dict] = None
    ) -> str:
        """Get the most prominent mood from the text"""
        mood_scores = self.detect_mood(text, additional_context)
        return max(mood_scores.items(), key=lambda x: x[1])[0]
