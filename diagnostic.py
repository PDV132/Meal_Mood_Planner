#!/usr/bin/env python3
"""
AI Mood Meal Assistant - Backend Diagnostic Script
This script helps identify why the backend server won't start
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Python Version Check")
    print("-" * 30)
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    else:
        print("✅ Python version compatible")
        return True

def check_required_packages():
    """Check if required packages are installed"""
    print("\n📦 Package Installation Check")
    print("-" * 30)
    
    required_packages = {
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'pydantic': 'pydantic',
        'numpy': 'numpy',
        'sklearn': 'scikit-learn',
        'sentence_transformers': 'sentence-transformers',
        'transformers': 'transformers',
        'torch': 'torch',
        'faiss': 'faiss-cpu',
        'librosa': 'librosa',
        'pickle': 'built-in',
        'json': 'built-in',
        'os': 'built-in',
        'datetime': 'built-in',
        'typing': 'built-in',
        'asyncio': 'built-in',
        'logging': 'built-in'
    }
    
    missing_packages = []
    
    for package, pip_name in required_packages.items():
        try:
            if pip_name == 'built-in':
                __import__(package)
                print(f"✅ {package} (built-in)")
            else:
                __import__(package)
                print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (install with: pip install {pip_name})")
            if pip_name != 'built-in':
                missing_packages.append(pip_name)
    
    return missing_packages

def check_required_files():
    """Check if all required files exist"""
    print("\n📁 Required Files Check")
    print("-" * 30)
    
    required_files = {
        'enhanced_backend.py': 'Main backend file',
        'vector_meal_engine.py': 'Vector search engine',
        'enhanced_mood_detector.py': 'Mood detection module',
        'enhanced_meal_suggester.py': 'Meal suggestion module',
        'meal.json': 'Meal data file'
    }
    
    missing_files = []
    
    for file, description in required_files.items():
        if Path(file).exists():
            print(f"✅ {file} - {description}")
        else:
            print(f"❌ {file} - {description}")
            missing_files.append(file)
    
    return missing_files

def create_minimal_dependencies():
    """Create minimal versions of missing dependency files"""
    print("\n🔧 Creating Minimal Dependencies")
    print("-" * 30)
    
    # Create speech_to_text.py
    if not Path("speech_to_text.py").exists():
        with open("speech_to_text.py", "w") as f:
            f.write("""
def transcribe_audio(audio_path: str) -> str:
    '''Simple fallback transcription'''
    return "I am feeling emotional and would like a meal recommendation"
""")
        print("✅ Created speech_to_text.py")
    
    # Create text_to_speech.py
    if not Path("text_to_speech.py").exists():
        with open("text_to_speech.py", "w") as f:
            f.write("""
def convert_text_to_speech(text: str) -> bytes:
    '''Simple fallback TTS'''
    return None
""")
        print("✅ Created text_to_speech.py")
    
    # Create minimal meal.json
    if not Path("meal.json").exists():
        minimal_meals = [
            {
                "meal_name": "Comfort Soup",
                "mood_1": "Sad",
                "mood_2": "Tired",
                "reason": "Warm and comforting",
                "benefit": "Provides warmth and nutrition",
                "calories": 200,
                "cultural_theme": "Comfort Food",
                "dietary_theme": "General"
            },
            {
                "meal_name": "Green Tea",
                "mood_1": "Anxious",
                "mood_2": "Restless",
                "reason": "Calming properties",
                "benefit": "Reduces stress and anxiety",
                "calories": 5,
                "cultural_theme": "Asian",
                "dietary_theme": "Light"
            }
        ]
        
        import json
        with open("meal.json", "w") as f:
            json.dump(minimal_meals, f, indent=2)
        print("✅ Created minimal meal.json")

def test_backend_import():
    """Test if the backend can be imported"""
    print("\n🧪 Backend Import Test")
    print("-" * 30)
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.getcwd())
        
        # Try to import the backend module
        import enhanced_backend
        print("✅ Backend module imported successfully")
        
        # Check if FastAPI app exists
        if hasattr(enhanced_backend, 'app'):
            print("✅ FastAPI app found")
            return True
        else:
            print("❌ FastAPI app not found in backend module")
            return False
            
    except Exception as e:
        print(f"❌ Backend import failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_manual_uvicorn():
    """Test running uvicorn manually with detailed output"""
    print("\n🚀 Manual Uvicorn Test")
    print("-" * 30)
    
    try:
        # Run uvicorn with detailed output
        cmd = [sys.executable, "-m", "uvicorn", "enhanced_backend:app", "--host", "127.0.0.1", "--port", "8000"]
        print(f"Running: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a few seconds and check output
        import time
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Uvicorn started successfully!")
            process.terminate()
            process.wait()
            return True
        else:
            stdout, stderr = process.communicate()
            print("❌ Uvicorn failed to start")
            print("STDOUT:", stdout[:500])
            print("STDERR:", stderr[:500])
            return False
            
    except Exception as e:
        print(f"❌ Manual uvicorn test failed: {str(e)}")
        return False

def install_missing_packages(packages):
    """Install missing packages"""
    if not packages:
        return True
    
    print(f"\n📥 Installing Missing Packages")
    print("-" * 30)
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package
            ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def create_simple_backend():
    """Create a simplified backend for testing"""
    print("\n🔧 Creating Simplified Backend")
    print("-" * 30)
    
    simple_backend = '''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from typing import Dict, List

app = FastAPI(title="Simple AI Mood Meal Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextMoodRequest(BaseModel):
    text: str
    user_id: str = "default"

class MoodRequest(BaseModel):
    mood1: str
    mood2: str
    user_id: str = "default"

# Load meal data
try:
    with open("meal.json", "r") as f:
        meals = json.load(f)
except:
    meals = [
        {
            "meal_name": "Comfort Soup",
            "mood_1": "Sad",
            "mood_2": "Tired",
            "reason": "Warm and comforting",
            "benefit": "Provides warmth and nutrition",
            "calories": 200,
            "cultural_theme": "Comfort Food",
            "dietary_theme": "General"
        }
    ]

@app.get("/")
async def root():
    return {"message": "Simple AI Mood Meal Assistant API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "meals_loaded": len(meals)}

@app.post("/suggest-meal-from-text")
async def suggest_meal_from_text(request: TextMoodRequest):
    # Simple mood detection
    text_lower = request.text.lower()
    if "sad" in text_lower or "down" in text_lower:
        mood1, mood2 = "Sad", "Tired"
    elif "anxious" in text_lower or "nervous" in text_lower:
        mood1, mood2 = "Anxious", "Restless"
    else:
        mood1, mood2 = "Calm", "Neutral"
    
    # Find matching meal
    for meal in meals:
        if meal.get("mood_1") == mood1 or meal.get("mood_2") == mood2:
            return {
                "meal": meal["meal_name"],
                "mood_detected": [mood1, mood2],
                "reason": meal["reason"],
                "benefit": meal["benefit"],
                "calories": meal.get("calories", "N/A"),
                "cultural_theme": meal.get("cultural_theme", "Mixed"),
                "explanation": f"Based on your mood, {meal['meal_name']} is recommended because {meal['reason']}."
            }
    
    # Fallback
    return {
        "meal": meals[0]["meal_name"],
        "mood_detected": [mood1, mood2],
        "reason": meals[0]["reason"],
        "benefit": meals[0]["benefit"],
        "calories": meals[0].get("calories", "N/A"),
        "cultural_theme": meals[0].get("cultural_theme", "Mixed"),
        "explanation": "A comforting meal to help with your current mood."
    }

@app.post("/suggest-meal-from-moods")
async def suggest_meal_from_moods(request: MoodRequest):
    # Find matching meal
    for meal in meals:
        if meal.get("mood_1") == request.mood1 or meal.get("mood_2") == request.mood2:
            return {
                "meal": meal["meal_name"],
                "reason": meal["reason"],
                "benefit": meal["benefit"],
                "calories": meal.get("calories", "N/A"),
                "cultural_theme": meal.get("cultural_theme", "Mixed")
            }
    
    # Fallback
    return {
        "meal": meals[0]["meal_name"],
        "reason": meals[0]["reason"],
        "benefit": meals[0]["benefit"],
        "calories": meals[0].get("calories", "N/A"),
        "cultural_theme": meals[0].get("cultural_theme", "Mixed")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    with open("simple_backend.py", "w") as f:
        f.write(simple_backend)
    
    print("✅ Created simple_backend.py")
    print("You can test with: python -m uvicorn simple_backend:app --host 0.0.0.0 --port 8000")

def main():
    """Main diagnostic function"""
    print("🔍 AI Mood Meal Assistant - Backend Diagnostics")
    print("=" * 50)
    
    # Check Python version
    python_ok = check_python_version()
    
    # Check packages
    missing_packages = check_required_packages()
    
    # Check files
    missing_files = check_required_files()
    
    # Create minimal dependencies
    create_minimal_dependencies()
    
    # Install missing packages if needed
    if missing_packages:
        install_ok = install_missing_packages(missing_packages)
        if not install_ok:
            print("\n❌ Failed to install some packages. Try installing manually:")
            for pkg in missing_packages:
                print(f"  pip install {pkg}")
    
    # Test backend import
    import_ok = test_backend_import()
    
    if not import_ok:
        print("\n🔧 The main backend has issues. Creating simplified version...")
        create_simple_backend()
        
        print("\n📋 Troubleshooting Summary")
        print("-" * 30)
        print("1. Try the simplified backend first:")
        print("   python -m uvicorn simple_backend:app --host 0.0.0.0 --port 8000")
        print()
        print("2. If that works, the issue is with the complex backend components")
        print("3. Common issues:")
        print("   - Heavy ML models (transformers, sentence-transformers)")
        print("   - FAISS installation problems")
        print("   - Missing model files")
        print()
        print("4. For production, you may need to:")
        print("   - Install PyTorch separately")
        print("   - Use CPU-only versions of models")
        print("   - Increase timeout for model loading")
    else:
        print("\n✅ Backend should work! Try starting with:")
        print("python -m uvicorn enhanced_backend:app --host 0.0.0.0 --port 8000")
    
    # Test manual uvicorn
    if not test_manual_uvicorn():
        print("\n❌ Manual uvicorn test also failed")
        print("Try the simplified backend instead")

if __name__ == "__main__":
    main()