from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import os
from typing import Dict, List, Tuple

class VectorMealEngine:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.meals = []
        
    def load_meals(self, meals_data: List[Dict]) -> None:
        """Load meals and create FAISS index for fast similarity search"""
        self.meals = meals_data
        
        # Create embeddings for all meals
        meal_texts = [
            f"{meal['name']} {meal['cuisine_type']} {meal['description']}"
            for meal in meals_data
        ]
        embeddings = self.model.encode(meal_texts, convert_to_tensor=True)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.numpy())
        
    def find_similar_meals(
        self, 
        mood_text: str, 
        k: int = 5
    ) -> List[Tuple[Dict, float]]:
        """Find meals similar to the given mood description"""
        # Create query embedding
        query_embedding = self.model.encode([mood_text])
        
        # Search in FAISS index
        distances, indices = self.index.search(query_embedding, k)
        
        # Return meals with their distances
        return [
            (self.meals[idx], float(dist))
            for idx, dist in zip(indices[0], distances[0])
        ]
        
    def save(self, path: str) -> None:
        """Save the meal engine state"""
        with open(path, "wb") as f:
            pickle.dump({
                "meals": self.meals,
                "index": faiss.serialize_index(self.index)
            }, f)
            
    def load(self, path: str) -> None:
        """Load the meal engine state"""
        with open(path, "rb") as f:
            data = pickle.load(f)
            self.meals = data["meals"]
            self.index = faiss.deserialize_index(data["index"])
