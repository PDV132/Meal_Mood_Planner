import json
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class EnhancedMealSuggester:
    def __init__(self, meal_data_path: str = "meal.json"):
        self.meal_data = self.load_meal_data(meal_data_path)
        self.preferences_file = "user_preferences.pkl"
        self.user_preferences = self.load_preferences()
        
        # Comprehensive mood categories with similarity mappings
        self.mood_mappings = {
            # Existing moods from meal.json
            'Sad': ['Sad', 'Melancholy', 'Depressed', 'Dejected', 'Heartbroken', 'Sorrowful', 'Mournful', 'Despondent', 'Blue', 'Down'],
            'Anxious': ['Anxious', 'Nervous', 'Worried', 'Tense', 'Apprehensive', 'Uneasy', 'Panicked', 'Stressed', 'Jittery', 'On edge'],
            'Tired': ['Tired', 'Exhausted', 'Fatigued', 'Weary', 'Drained', 'Burnt out', 'Sleepy', 'Drowsy', 'Lethargic', 'Worn out'],
            'Restless': ['Restless', 'Fidgety', 'Antsy', 'Hyperactive', 'Agitated', 'Unsettled', 'Impatient', 'Edgy', 'Wired', 'Keyed up'],
            'Irritable': ['Irritable', 'Annoyed', 'Frustrated', 'Grumpy', 'Cranky', 'Moody', 'Snappy', 'Short-tempered', 'Testy', 'Prickly'],
            'Overwhelmed': ['Overwhelmed', 'Swamped', 'Burdened', 'Pressured', 'Stressed out', 'Overloaded', 'Inundated', 'Snowed under', 'Maxed out', 'At capacity'],
            'Foggy': ['Foggy', 'Confused', 'Unclear', 'Muddled', 'Hazy', 'Cloudy', 'Bewildered', 'Perplexed', 'Disoriented', 'Spacey'],
            'Lonely': ['Lonely', 'Isolated', 'Alone', 'Solitary', 'Abandoned', 'Forsaken', 'Disconnected', 'Cut off', 'Estranged', 'Friendless'],
            'Gloomy': ['Gloomy', 'Dark', 'Bleak', 'Dismal', 'Dreary', 'Somber', 'Morose', 'Sullen', 'Brooding', 'Pessimistic'],
            'Sluggish': ['Sluggish', 'Slow', 'Lazy', 'Inactive', 'Torpid', 'Listless', 'Languid', 'Apathetic', 'Indolent', 'Slothful'],
            'Unfocused': ['Unfocused', 'Distracted', 'Scattered', 'Absent-minded', 'Inattentive', 'Preoccupied', 'Daydreaming', 'Wandering', 'Disorganized', 'All over the place'],
            'Distracted': ['Distracted', 'Unfocused', 'Scattered', 'Preoccupied', 'Absent-minded', 'Inattentive', 'Diverted', 'Sidetracked', 'Off-task', 'Mind elsewhere'],
            'Moody': ['Moody', 'Temperamental', 'Changeable', 'Volatile', 'Unpredictable', 'Erratic', 'Fickle', 'Capricious', 'Mercurial', 'Up and down'],
            'Homesick': ['Homesick', 'Nostalgic', 'Yearning', 'Longing', 'Missing home', 'Wistful', 'Pining', 'Aching for home', 'Sentimental', 'Reminiscent'],
            'Cold': ['Cold', 'Chilly', 'Freezing', 'Shivering', 'Frigid', 'Icy', 'Frosty', 'Numb with cold', 'Frozen', 'Bitter cold'],
            'Grumpy': ['Grumpy', 'Cranky', 'Surly', 'Cantankerous', 'Crabby', 'Peevish', 'Petulant', 'Sulky', 'Bad-tempered', 'Ornery'],
            'Bored': ['Bored', 'Uninterested', 'Apathetic', 'Indifferent', 'Disengaged', 'Unstimulated', 'Tedious', 'Monotonous', 'Dull', 'Lifeless'],
            'Numb': ['Numb', 'Emotionless', 'Detached', 'Disconnected', 'Unfeeling', 'Insensitive', 'Deadened', 'Vacant', 'Empty', 'Hollow'],
            
            # Extended positive moods
            'Happy': ['Happy', 'Joyful', 'Cheerful', 'Glad', 'Delighted', 'Pleased', 'Content', 'Satisfied', 'Upbeat', 'Positive'],
            'Excited': ['Excited', 'Thrilled', 'Elated', 'Ecstatic', 'Euphoric', 'Exhilarated', 'Enthusiastic', 'Pumped', 'Stoked', 'Amped'],
            'Energized': ['Energized', 'Vibrant', 'Dynamic', 'Lively', 'Spirited', 'Animated', 'Vigorous', 'Peppy', 'Zippy', 'Full of life'],
            'Calm': ['Calm', 'Peaceful', 'Serene', 'Tranquil', 'Relaxed', 'Composed', 'Centered', 'Balanced', 'Still', 'Quiet'],
            'Confident': ['Confident', 'Self-assured', 'Certain', 'Secure', 'Poised', 'Bold', 'Assertive', 'Strong', 'Empowered', 'Sure'],
            'Motivated': ['Motivated', 'Driven', 'Determined', 'Ambitious', 'Goal-oriented', 'Focused', 'Inspired', 'Purposeful', 'Committed', 'Dedicated'],
            'Grateful': ['Grateful', 'Thankful', 'Appreciative', 'Blessed', 'Fortunate', 'Indebted', 'Obliged', 'Touched', 'Moved', 'Humbled'],
            'Hopeful': ['Hopeful', 'Optimistic', 'Positive', 'Encouraging', 'Uplifting', 'Promising', 'Bright', 'Sunny', 'Rosy', 'Confident about future'],
            'Curious': ['Curious', 'Inquisitive', 'Interested', 'Intrigued', 'Fascinated', 'Wondering', 'Questioning', 'Exploring', 'Investigative', 'Eager to learn'],
            'Playful': ['Playful', 'Fun-loving', 'Lighthearted', 'Whimsical', 'Mischievous', 'Jovial', 'Spirited', 'Bubbly', 'Giggly', 'Carefree'],
            'Inspired': ['Inspired', 'Creative', 'Imaginative', 'Innovative', 'Artistic', 'Visionary', 'Inventive', 'Original', 'Brilliant', 'Enlightened'],
            'Proud': ['Proud', 'Accomplished', 'Successful', 'Triumphant', 'Victorious', 'Satisfied', 'Fulfilled', 'Achieved', 'Honored', 'Distinguished'],
            'Loved': ['Loved', 'Cherished', 'Adored', 'Valued', 'Appreciated', 'Treasured', 'Beloved', 'Dear', 'Precious', 'Special'],
            'Adventurous': ['Adventurous', 'Daring', 'Bold', 'Brave', 'Courageous', 'Fearless', 'Intrepid', 'Audacious', 'Venturesome', 'Risk-taking'],
            
            # Complex emotional states
            'Conflicted': ['Conflicted', 'Torn', 'Ambivalent', 'Uncertain', 'Indecisive', 'Mixed feelings', 'Confused', 'Divided', 'Unsure', 'Wavering'],
            'Vulnerable': ['Vulnerable', 'Exposed', 'Fragile', 'Sensitive', 'Delicate', 'Tender', 'Raw', 'Open', 'Unprotected', 'At risk'],
            'Overwhelmed with joy': ['Overwhelmed with joy', 'Overjoyed', 'Blissful', 'Rapturous', 'In seventh heaven', 'On cloud nine', 'Walking on air', 'Over the moon', 'Thrilled beyond words', 'Bursting with happiness'],
            'Melancholic': ['Melancholic', 'Wistful', 'Pensive', 'Reflective', 'Contemplative', 'Thoughtful', 'Introspective', 'Brooding', 'Musing', 'Lost in thought'],
            'Frustrated': ['Frustrated', 'Exasperated', 'Vexed', 'Irked', 'Aggravated', 'Annoyed', 'Bothered', 'Perturbed', 'Riled up', 'Fed up'],
            'Disappointed': ['Disappointed', 'Let down', 'Disillusioned', 'Disheartened', 'Discouraged', 'Deflated', 'Crestfallen', 'Downcast', 'Dismayed', 'Upset'],
            'Embarrassed': ['Embarrassed', 'Ashamed', 'Humiliated', 'Mortified', 'Sheepish', 'Red-faced', 'Flustered', 'Awkward', 'Self-conscious', 'Uncomfortable'],
            'Jealous': ['Jealous', 'Envious', 'Resentful', 'Covetous', 'Green with envy', 'Bitter', 'Spiteful', 'Grudging', 'Possessive', 'Suspicious'],
            'Guilty': ['Guilty', 'Remorseful', 'Regretful', 'Sorry', 'Repentant', 'Contrite', 'Penitent', 'Conscience-stricken', 'Ashamed', 'Self-reproachful'],
            'Relieved': ['Relieved', 'Unburdened', 'Freed', 'Liberated', 'Lightened', 'Eased', 'Comforted', 'Reassured', 'At peace', 'Stress-free'],
            'Surprised': ['Surprised', 'Astonished', 'Amazed', 'Shocked', 'Stunned', 'Startled', 'Taken aback', 'Flabbergasted', 'Bewildered', 'Caught off guard'],
            'Disgusted': ['Disgusted', 'Revolted', 'Repulsed', 'Nauseated', 'Sickened', 'Appalled', 'Horrified', 'Offended', 'Turned off', 'Put off'],
            
            # Physical/Mental states
            'Mentally fatigued': ['Mentally fatigued', 'Brain fog', 'Cognitively drained', 'Mentally exhausted', 'Burnt out mentally', 'Intellectually tired', 'Mind weary', 'Thinking slowly', 'Mental fatigue', 'Cognitively overloaded'],
            'Physically drained': ['Physically drained', 'Body tired', 'Muscle fatigue', 'Physically exhausted', 'Bodily worn out', 'Sore', 'Aching', 'Physically spent', 'Body weary', 'Physically depleted'],
            'Alert': ['Alert', 'Sharp', 'Focused', 'Attentive', 'Aware', 'Vigilant', 'Keen', 'Acute', 'On the ball', 'Switched on'],
            'Hyperactive': ['Hyperactive', 'Manic', 'Frenzied', 'Frenetic', 'Overexcited', 'Wired', 'Hyper', 'Bouncing off walls', 'Can\'t sit still', 'Overstimulated'],
            'Spacey': ['Spacey', 'Absent-minded', 'Dreamy', 'In a daze', 'Out of it', 'Not all there', 'Disconnected', 'Floating', 'Head in clouds', 'Zoned out'],
            'Tense': ['Tense', 'Tight', 'Wound up', 'Stiff', 'Rigid', 'Uptight', 'Stressed', 'Strained', 'Coiled', 'On edge'],
            'Relaxed': ['Relaxed', 'Loose', 'Easy-going', 'Laid-back', 'Chill', 'Mellow', 'Casual', 'Unhurried', 'At ease', 'Comfortable'],
            
            # Social/Relational moods
            'Sociable': ['Sociable', 'Outgoing', 'Friendly', 'Gregarious', 'Extroverted', 'People-person', 'Social butterfly', 'Warm', 'Approachable', 'Welcoming'],
            'Antisocial': ['Antisocial', 'Withdrawn', 'Reclusive', 'Hermit-like', 'Introverted', 'Solitary', 'Unsociable', 'Standoffish', 'Aloof', 'Distant'],
            'Affectionate': ['Affectionate', 'Loving', 'Caring', 'Tender', 'Warm', 'Cuddly', 'Huggy', 'Demonstrative', 'Expressive', 'Nurturing'],
            'Needy': ['Needy', 'Clingy', 'Dependent', 'Attention-seeking', 'Demanding', 'High-maintenance', 'Insecure', 'Requiring validation', 'Codependent', 'Possessive'],
            
            # Temporal/Nostalgic moods
            'Nostalgic': ['Nostalgic', 'Reminiscent', 'Sentimental', 'Wistful', 'Looking back', 'Missing the past', 'Longing for old times', 'Remembering fondly', 'Yearning for yesterday', 'Living in memories'],
            'Anticipatory': ['Anticipatory', 'Expectant', 'Waiting', 'Looking forward', 'Eager', 'Excited about future', 'Hopeful', 'Preparing', 'Ready', 'On standby'],
            
            # Creative/Intellectual moods
            'Creative': ['Creative', 'Artistic', 'Imaginative', 'Innovative', 'Inventive', 'Original', 'Inspired', 'Visionary', 'Expressive', 'Resourceful'],
            'Analytical': ['Analytical', 'Logical', 'Rational', 'Methodical', 'Systematic', 'Critical thinking', 'Problem-solving', 'Reasoning', 'Calculating', 'Objective'],
            'Intuitive': ['Intuitive', 'Instinctive', 'Gut feeling', 'Sensing', 'Perceptive', 'Insightful', 'Empathetic', 'Feeling-based', 'Sixth sense', 'Inner knowing']
        }
        
        # Initialize TF-IDF vectorizer for semantic similarity
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        self._build_mood_vectors()
    
    def load_meal_data(self, filepath: str) -> List[Dict]:
        """Load meal data from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading meal data: {e}")
            return []
    
    def load_preferences(self) -> Dict:
        """Load user preferences from file"""
        try:
            if os.path.exists(self.preferences_file):
                with open(self.preferences_file, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            print(f"Error loading preferences: {e}")
        return {}
    
    def _build_mood_vectors(self):
        """Build TF-IDF vectors for mood similarity matching"""
        try:
            # Create corpus of all mood descriptions
            mood_corpus = []
            self.mood_labels = []
            
            for main_mood, similar_moods in self.mood_mappings.items():
                mood_text = ' '.join(similar_moods)
                mood_corpus.append(mood_text)
                self.mood_labels.append(main_mood)
            
            # Fit TF-IDF vectorizer
            self.mood_vectors = self.vectorizer.fit_transform(mood_corpus)
            
        except Exception as e:
            print(f"Error building mood vectors: {e}")
            self.mood_vectors = None
    
    def find_similar_mood(self, input_mood: str, threshold: float = 0.3) -> Tuple[str, str]:
        """Find the most similar mood from available categories"""
        try:
            # Direct match first
            for main_mood, similar_moods in self.mood_mappings.items():
                if input_mood.lower() in [m.lower() for m in similar_moods]:
                    return main_mood, main_mood
            
            # Semantic similarity matching
            if self.mood_vectors is not None:
                input_vector = self.vectorizer.transform([input_mood])
                similarities = cosine_similarity(input_vector, self.mood_vectors)[0]
                
                # Find best matches
                best_indices = np.argsort(similarities)[::-1]
                
                if similarities[best_indices[0]] > threshold:
                    primary_mood = self.mood_labels[best_indices[0]]
                    secondary_mood = self.mood_labels[best_indices[1]] if len(best_indices) > 1 else primary_mood
                    return primary_mood, secondary_mood
            
            # Fallback to default
            return "Calm", "Neutral"
            
        except Exception as e:
            print(f"Error in mood similarity matching: {e}")
            return "Calm", "Neutral"
    
    def suggest_meal(self, mood1: str, mood2: str, user_id: str = "default") -> Dict:
        """Enhanced meal suggestion with preference consideration"""
        try:
            # Map input moods to available categories
            mapped_mood1, _ = self.find_similar_mood(mood1)
            mapped_mood2, _ = self.find_similar_mood(mood2)
            
            # Get user preferences
            user_prefs = self.user_preferences.get(user_id, {})
            dietary_restrictions = user_prefs.get('dietary_restrictions', [])
            cultural_preferences = user_prefs.get('cultural_preferences', [])
            mood_preferences = user_prefs.get('mood_preferences', {})
            
            # Find matching meals
            matching_meals = []
            for meal in self.meal_data:
                if (meal["mood_1"] == mapped_mood1 and meal["mood_2"] == mapped_mood2) or \
                   (meal["mood_1"] == mapped_mood2 and meal["mood_2"] == mapped_mood1):
                    matching_meals.append(meal)
            
            # If no exact match, find meals with at least one matching mood
            if not matching_meals:
                for meal in self.meal_data:
                    if meal["mood_1"] in [mapped_mood1, mapped_mood2] or \
                       meal["mood_2"] in [mapped_mood1, mapped_mood2]:
                        matching_meals.append(meal)
            
            # Filter by dietary restrictions
            if dietary_restrictions:
                filtered_meals = []
                for meal in matching_meals:
                    dietary_theme = meal.get("dietary_theme", "").lower()
                    if not any(restriction.lower() in dietary_theme for restriction in dietary_restrictions):
                        filtered_meals.append(meal)
                if filtered_meals:
                    matching_meals = filtered_meals
            
            # Prioritize by cultural preferences
            if cultural_preferences and matching_meals:
                preferred_meals = []
                other_meals = []
                for meal in matching_meals:
                    cultural_theme = meal.get("cultural_theme", "").lower()
                    if any(pref.lower() in cultural_theme for pref in cultural_preferences):
                        preferred_meals.append(meal)
                    else:
                        other_meals.append(meal)
                matching_meals = preferred_meals + other_meals
            
            # Prioritize by user's past preferences
            mood_key = f"{mapped_mood1}_{mapped_mood2}"
            if mood_key in mood_preferences:
                preferred_meal_names = mood_preferences[mood_key]
                preferred_meals = [m for m in matching_meals if m["meal_name"] in preferred_meal_names]
                other_meals = [m for m in matching_meals if m["meal_name"] not in preferred_meal_names]
                matching_meals = preferred_meals + other_meals
            
            # Select the best meal
            if matching_meals:
                selected_meal = matching_meals[0]
                return {
                    "meal": selected_meal["meal_name"],
                    "mood_detected": [mapped_mood1, mapped_mood2],
                    "original_moods": [mood1, mood2],
                    "reason": selected_meal["reason"],
                    "benefit": selected_meal["benefit"],
                    "calories": selected_meal["calories"],
                    "cultural_theme": selected_meal.get("cultural_theme", ""),
                    "dietary_theme": selected_meal.get("dietary_theme", ""),
                    "confidence": "High" if (mapped_mood1 == mood1 and mapped_mood2 == mood2) else "Medium"
                }
            else:
                # Fallback suggestion
                fallback_meal = self.meal_data[0] if self.meal_data else None
                if fallback_meal:
                    return {
                        "meal": fallback_meal["meal_name"],
                        "mood_detected": [mapped_mood1, mapped_mood2],
                        "original_moods": [mood1, mood2],
                        "reason": "A comforting meal to help balance your current emotional state",
                        "benefit": fallback_meal["benefit"],
                        "calories": fallback_meal["calories"],
                        "cultural_theme": fallback_meal.get("cultural_theme", ""),
                        "dietary_theme": fallback_meal.get("dietary_theme", ""),
                        "confidence": "Low"
                    }
                else:
                    return {"error": "No meals available in database"}
                    
        except Exception as e:
            print(f"Error in meal suggestion: {e}")
            return {"error": f"Error generating meal suggestion: {str(e)}"}
    
    def get_mood_suggestions(self, partial_mood: str, limit: int = 10) -> List[str]:
        """Get mood suggestions for autocomplete"""
        suggestions = []
        partial_lower = partial_mood.lower()
        
        for main_mood, similar_moods in self.mood_mappings.items():
            for mood in similar_moods:
                if partial_lower in mood.lower() and mood not in suggestions:
                    suggestions.append(mood)
                    if len(suggestions) >= limit:
                        return suggestions
        
        return suggestions
    
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
        
        # Update mood preferences for highly rated meals
        if mood_key not in self.user_preferences[user_id]['mood_preferences']:
            self.user_preferences[user_id]['mood_preferences'][mood_key] = []
        
        if rating >= 4:  # Good rating
            if meal_name not in self.user_preferences[user_id]['mood_preferences'][mood_key]:
                self.user_preferences[user_id]['mood_preferences'][mood_key].append(meal_name)
        elif rating <= 2:  # Poor rating
            if meal_name in self.user_preferences[user_id]['mood_preferences'][mood_key]:
                self.user_preferences[user_id]['mood_preferences'][mood_key].remove(meal_name)
        
        self.user_preferences[user_id]['last_updated'] = datetime.now().isoformat()
        self.save_preferences()
    
    def save_preferences(self):
        """Save user preferences to file"""
        try:
            with open(self.preferences_file, 'wb') as f:
                pickle.dump(self.user_preferences, f)
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
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
