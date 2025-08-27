import numpy as np
import faiss
import pickle
import json
import os
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorMealEngine:
    def __init__(self, meal_data_path: str = "meal.json"):
        """Initialize the vector-based meal recommendation engine"""
        
        # Load sentence transformer for embeddings
        logger.info("Loading sentence transformer model...")
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load small language model for text generation
        logger.info("Loading small language model...")
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
        self.language_model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")
        
        # Alternative: Use a smaller, faster model
        try:
            self.text_generator = pipeline(
                "text-generation",
                model="distilgpt2",
                tokenizer="distilgpt2",
                max_length=150,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=50256
            )
        except Exception as e:
            logger.warning(f"Could not load text generation model: {e}")
            self.text_generator = None
        
        # Load meal data
        self.meal_data = self.load_meal_data(meal_data_path)
        
        # Initialize FAISS index
        self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
        self.faiss_index = None
        self.meal_embeddings = None
        self.meal_texts = []
        
        # Build vector index
        self.build_vector_index()
        
        # Enhanced mood mappings with semantic descriptions
        self.mood_descriptions = {
            'Sad': "feeling down, melancholy, blue, sorrowful, dejected, heartbroken, depressed, gloomy",
            'Anxious': "worried, nervous, stressed, tense, apprehensive, uneasy, panicked, jittery, on edge",
            'Tired': "exhausted, fatigued, weary, drained, sleepy, drowsy, lethargic, worn out, burnt out",
            'Restless': "fidgety, antsy, hyperactive, agitated, unsettled, impatient, edgy, wired, keyed up",
            'Irritable': "annoyed, frustrated, grumpy, cranky, moody, snappy, short-tempered, testy, prickly",
            'Overwhelmed': "swamped, burdened, pressured, stressed out, overloaded, inundated, maxed out",
            'Foggy': "confused, unclear, muddled, hazy, cloudy, bewildered, perplexed, disoriented, spacey",
            'Lonely': "isolated, alone, solitary, abandoned, forsaken, disconnected, cut off, estranged",
            'Gloomy': "dark, bleak, dismal, dreary, somber, morose, sullen, brooding, pessimistic",
            'Sluggish': "slow, lazy, inactive, torpid, listless, languid, apathetic, indolent, slothful",
            'Unfocused': "distracted, scattered, absent-minded, inattentive, preoccupied, daydreaming",
            'Happy': "joyful, cheerful, glad, delighted, pleased, content, satisfied, upbeat, positive",
            'Excited': "thrilled, elated, ecstatic, euphoric, exhilarated, enthusiastic, pumped, stoked",
            'Energized': "vibrant, dynamic, lively, spirited, animated, vigorous, peppy, zippy, full of life",
            'Calm': "peaceful, serene, tranquil, relaxed, composed, centered, balanced, still, quiet",
            'Confident': "self-assured, certain, secure, poised, bold, assertive, strong, empowered, sure",
            'Motivated': "driven, determined, ambitious, goal-oriented, focused, inspired, purposeful",
            'Grateful': "thankful, appreciative, blessed, fortunate, indebted, obliged, touched, moved",
            'Hopeful': "optimistic, positive, encouraging, uplifting, promising, bright, sunny, rosy",
            'Curious': "inquisitive, interested, intrigued, fascinated, wondering, questioning, exploring",
            'Playful': "fun-loving, lighthearted, whimsical, mischievous, jovial, spirited, bubbly, giggly"
        }
        
        # Cache for embeddings
        self.mood_embeddings_cache = {}
        self.build_mood_embeddings()
        
        logger.info("Vector meal engine initialized successfully!")
    
    def load_meal_data(self, filepath: str) -> List[Dict]:
        """Load meal data from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading meal data: {e}")
            return []
    
    def build_vector_index(self):
        """Build FAISS vector index for meal recommendations"""
        try:
            logger.info("Building FAISS vector index...")
            
            # Create text descriptions for each meal
            for meal in self.meal_data:
                meal_text = f"{meal['meal_name']} {meal['reason']} {meal['benefit']} {meal['cultural_theme']} {meal['dietary_theme']} mood {meal['mood_1']} {meal['mood_2']}"
                self.meal_texts.append(meal_text)
            
            # Generate embeddings for all meals
            logger.info("Generating meal embeddings...")
            self.meal_embeddings = self.sentence_model.encode(self.meal_texts)
            
            # Create FAISS index
            self.faiss_index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for cosine similarity
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(self.meal_embeddings)
            
            # Add embeddings to index
            self.faiss_index.add(self.meal_embeddings.astype('float32'))
            
            logger.info(f"FAISS index built with {len(self.meal_data)} meals")
            
            # Save index for future use
            self.save_index()
            
        except Exception as e:
            logger.error(f"Error building vector index: {e}")
    
    def build_mood_embeddings(self):
        """Pre-compute embeddings for mood descriptions"""
        try:
            logger.info("Building mood embeddings...")
            for mood, description in self.mood_descriptions.items():
                embedding = self.sentence_model.encode([description])
                faiss.normalize_L2(embedding)
                self.mood_embeddings_cache[mood] = embedding[0]
            logger.info("Mood embeddings built successfully")
        except Exception as e:
            logger.error(f"Error building mood embeddings: {e}")
    
    def save_index(self, index_path: str = "meal_faiss_index.bin"):
        """Save FAISS index to disk"""
        try:
            faiss.write_index(self.faiss_index, index_path)
            
            # Save meal data and embeddings
            with open("meal_embeddings.pkl", "wb") as f:
                pickle.dump({
                    'meal_embeddings': self.meal_embeddings,
                    'meal_texts': self.meal_texts,
                    'meal_data': self.meal_data
                }, f)
            
            logger.info("FAISS index and embeddings saved")
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    def load_index(self, index_path: str = "meal_faiss_index.bin"):
        """Load FAISS index from disk"""
        try:
            if os.path.exists(index_path) and os.path.exists("meal_embeddings.pkl"):
                self.faiss_index = faiss.read_index(index_path)
                
                with open("meal_embeddings.pkl", "rb") as f:
                    data = pickle.load(f)
                    self.meal_embeddings = data['meal_embeddings']
                    self.meal_texts = data['meal_texts']
                    self.meal_data = data['meal_data']
                
                logger.info("FAISS index loaded from disk")
                return True
        except Exception as e:
            logger.error(f"Error loading index: {e}")
        return False
    
    def encode_mood_query(self, mood_text: str, mood1: str = None, mood2: str = None) -> np.ndarray:
        """Encode mood query into vector representation"""
        try:
            # Combine text description with mood keywords
            query_parts = [mood_text]
            
            if mood1 and mood1 in self.mood_descriptions:
                query_parts.append(self.mood_descriptions[mood1])
            
            if mood2 and mood2 in self.mood_descriptions:
                query_parts.append(self.mood_descriptions[mood2])
            
            query_text = " ".join(query_parts)
            
            # Generate embedding
            query_embedding = self.sentence_model.encode([query_text])
            faiss.normalize_L2(query_embedding)
            
            return query_embedding[0]
            
        except Exception as e:
            logger.error(f"Error encoding mood query: {e}")
            return np.zeros(self.embedding_dim)
    
    def vector_search(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[int, float]]:
        """Perform vector similarity search using FAISS"""
        try:
            if self.faiss_index is None:
                logger.error("FAISS index not initialized")
                return []
            
            # Search for similar meals
            query_embedding = query_embedding.reshape(1, -1).astype('float32')
            scores, indices = self.faiss_index.search(query_embedding, k)
            
            # Return list of (index, score) tuples
            results = [(int(indices[0][i]), float(scores[0][i])) for i in range(len(indices[0]))]
            return results
            
        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            return []
    
    def generate_explanation(self, meal: Dict, mood_text: str, mood1: str, mood2: str) -> str:
        """Generate explanation using small language model"""
        try:
            if self.text_generator is None:
                return self.generate_simple_explanation(meal, mood_text, mood1, mood2)
            
            # Create prompt for text generation
            prompt = f"You are feeling {mood1} and {mood2}. The recommended meal is {meal['meal_name']}. This meal helps because {meal['reason']} and provides {meal['benefit']}. Here's why this is perfect for you:"
            
            # Generate explanation
            generated = self.text_generator(
                prompt,
                max_length=len(prompt.split()) + 50,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=50256
            )
            
            # Extract generated text
            full_text = generated[0]['generated_text']
            explanation = full_text[len(prompt):].strip()
            
            # Clean up the explanation
            if explanation:
                # Remove incomplete sentences
                sentences = explanation.split('.')
                complete_sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
                if complete_sentences:
                    explanation = '. '.join(complete_sentences[:2]) + '.'
                else:
                    explanation = self.generate_simple_explanation(meal, mood_text, mood1, mood2)
            else:
                explanation = self.generate_simple_explanation(meal, mood_text, mood1, mood2)
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return self.generate_simple_explanation(meal, mood_text, mood1, mood2)
    
    def generate_simple_explanation(self, meal: Dict, mood_text: str, mood1: str, mood2: str) -> str:
        """Generate a simple rule-based explanation"""
        explanations = [
            f"When you're feeling {mood1.lower()} and {mood2.lower()}, your body needs specific nutrients to help restore balance.",
            f"{meal['meal_name']} is an excellent choice because {meal['reason'].lower()}",
            f"The nutritional benefits include {meal['benefit'].lower()}, which directly addresses your current emotional state.",
            f"This {meal.get('cultural_theme', 'comforting')} dish provides {meal.get('calories', 'adequate')} calories to fuel your recovery.",
            "Remember, food is medicine for both body and mind. Take time to enjoy each bite mindfully."
        ]
        
        return " ".join(explanations[:3])  # Return first 3 sentences
    
    def recommend_meals(self, mood_text: str, mood1: str = None, mood2: str = None, 
                       user_preferences: Dict = None, k: int = 3) -> List[Dict]:
        """Get meal recommendations using vector search"""
        try:
            # Encode the mood query
            query_embedding = self.encode_mood_query(mood_text, mood1, mood2)
            
            # Perform vector search
            search_results = self.vector_search(query_embedding, k=k*2)  # Get more results for filtering
            
            recommendations = []
            
            for idx, score in search_results:
                if idx < len(self.meal_data):
                    meal = self.meal_data[idx].copy()
                    meal['similarity_score'] = score
                    meal['explanation'] = self.generate_explanation(meal, mood_text, mood1 or "", mood2 or "")
                    recommendations.append(meal)
            
            # Filter by user preferences if provided
            if user_preferences:
                recommendations = self.filter_by_preferences(recommendations, user_preferences)
            
            # Return top k recommendations
            return recommendations[:k]
            
        except Exception as e:
            logger.error(f"Error in meal recommendation: {e}")
            return []
    
    def filter_by_preferences(self, meals: List[Dict], preferences: Dict) -> List[Dict]:
        """Filter meals based on user preferences"""
        try:
            dietary_restrictions = preferences.get('dietary_restrictions', [])
            cultural_preferences = preferences.get('cultural_preferences', [])
            
            filtered_meals = []
            
            for meal in meals:
                # Check dietary restrictions
                dietary_theme = meal.get('dietary_theme', '').lower()
                if dietary_restrictions:
                    # Skip meals that conflict with dietary restrictions
                    conflicts = any(restriction.lower() in dietary_theme for restriction in dietary_restrictions)
                    if conflicts:
                        continue
                
                # Boost score for cultural preferences
                cultural_theme = meal.get('cultural_theme', '').lower()
                if cultural_preferences:
                    cultural_match = any(pref.lower() in cultural_theme for pref in cultural_preferences)
                    if cultural_match:
                        meal['similarity_score'] += 0.1  # Boost preferred cuisines
                
                filtered_meals.append(meal)
            
            # Re-sort by similarity score
            filtered_meals.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return filtered_meals
            
        except Exception as e:
            logger.error(f"Error filtering by preferences: {e}")
            return meals
    
    def get_mood_suggestions(self, partial_text: str, limit: int = 10) -> List[str]:
        """Get mood suggestions using vector similarity"""
        try:
            if len(partial_text) < 2:
                return []
            
            # Encode partial text
            query_embedding = self.sentence_model.encode([partial_text])
            faiss.normalize_L2(query_embedding)
            
            # Find similar moods
            suggestions = []
            for mood, embedding in self.mood_embeddings_cache.items():
                similarity = np.dot(query_embedding[0], embedding)
                if similarity > 0.3:  # Threshold for relevance
                    suggestions.append((mood, similarity))
            
            # Sort by similarity and return top suggestions
            suggestions.sort(key=lambda x: x[1], reverse=True)
            return [mood for mood, _ in suggestions[:limit]]
            
        except Exception as e:
            logger.error(f"Error getting mood suggestions: {e}")
            return []
    
    def update_meal_feedback(self, meal_name: str, rating: int, mood_context: str):
        """Update meal recommendations based on user feedback"""
        try:
            # Find the meal in our data
            meal_idx = None
            for i, meal in enumerate(self.meal_data):
                if meal['meal_name'] == meal_name:
                    meal_idx = i
                    break
            
            if meal_idx is not None:
                # Adjust embedding based on feedback
                if rating >= 4:  # Positive feedback
                    # Slightly boost this meal's embedding towards the mood context
                    mood_embedding = self.sentence_model.encode([mood_context])
                    faiss.normalize_L2(mood_embedding)
                    
                    # Weighted average to adjust meal embedding
                    alpha = 0.1  # Learning rate
                    self.meal_embeddings[meal_idx] = (
                        (1 - alpha) * self.meal_embeddings[meal_idx] + 
                        alpha * mood_embedding[0]
                    )
                    
                    # Normalize and update index
                    faiss.normalize_L2(self.meal_embeddings[meal_idx:meal_idx+1])
                    
                    # Update the FAISS index
                    self.faiss_index = faiss.IndexFlatIP(self.embedding_dim)
                    self.faiss_index.add(self.meal_embeddings.astype('float32'))
                    
                    logger.info(f"Updated embedding for {meal_name} based on positive feedback")
                
        except Exception as e:
            logger.error(f"Error updating meal feedback: {e}")
    
    def get_similar_meals(self, meal_name: str, k: int = 5) -> List[Dict]:
        """Find meals similar to a given meal"""
        try:
            # Find the meal index
            meal_idx = None
            for i, meal in enumerate(self.meal_data):
                if meal['meal_name'] == meal_name:
                    meal_idx = i
                    break
            
            if meal_idx is None:
                return []
            
            # Get the meal's embedding
            meal_embedding = self.meal_embeddings[meal_idx:meal_idx+1]
            
            # Search for similar meals
            scores, indices = self.faiss_index.search(meal_embedding.astype('float32'), k+1)  # +1 to exclude self
            
            similar_meals = []
            for i in range(1, len(indices[0])):  # Skip first result (self)
                idx = int(indices[0][i])
                if idx < len(self.meal_data):
                    meal = self.meal_data[idx].copy()
                    meal['similarity_score'] = float(scores[0][i])
                    similar_meals.append(meal)
            
            return similar_meals
            
        except Exception as e:
            logger.error(f"Error finding similar meals: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector engine"""
        return {
            'total_meals': len(self.meal_data),
            'embedding_dimension': self.embedding_dim,
            'index_size': self.faiss_index.ntotal if self.faiss_index else 0,
            'mood_categories': len(self.mood_descriptions),
            'model_info': {
                'sentence_transformer': 'all-MiniLM-L6-v2',
                'language_model': 'distilgpt2',
                'embedding_model_size': '22MB',
                'language_model_size': '82MB'
            }
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize the vector engine
    engine = VectorMealEngine()
    
    # Test mood-based recommendations
    test_mood = "I'm feeling really anxious about my presentation tomorrow and quite tired from staying up late"
    recommendations = engine.recommend_meals(test_mood, "Anxious", "Tired", k=3)
    
    print("Mood-based recommendations:")
    for i, meal in enumerate(recommendations, 1):
        print(f"{i}. {meal['meal_name']} (Score: {meal['similarity_score']:.3f})")
        print(f"   Reason: {meal['reason']}")
        print(f"   Explanation: {meal['explanation']}")
        print()
    
    # Test mood suggestions
    mood_suggestions = engine.get_mood_suggestions("anxi", limit=5)
    print("Mood suggestions for 'anxi':", mood_suggestions)
    
    # Test similar meals
    if recommendations:
        similar = engine.get_similar_meals(recommendations[0]['meal_name'], k=3)
        print(f"\nMeals similar to {recommendations[0]['meal_name']}:")
        for meal in similar:
            print(f"- {meal['meal_name']} (Score: {meal['similarity_score']:.3f})")
    
    # Print stats
    stats = engine.get_stats()
    print("\nEngine Statistics:")
    for key, value in stats.items():
        print(f"{key}: {value}")
