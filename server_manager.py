#!/usr/bin/env python3
"""
AI Mood Meal Assistant - Server Manager
This script helps manage the backend and frontend servers
"""

import subprocess
import sys
import time
import requests
import threading
import os
from pathlib import Path

class ServerManager:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:8501"
    
    def check_dependencies(self):
        """Check if required files exist"""
        required_files = [
            "enhanced_backend.py",
            "enhanced_app.py",
            "meal.json",
            "vector_meal_engine.py",
            "enhanced_mood_detector.py",
            "enhanced_meal_suggester.py"
        ]
        
        missing_files = []
        for file in required_files:
            if not Path(file).exists():
                missing_files.append(file)
        
        if missing_files:
            print("❌ Missing required files:")
            for file in missing_files:
                print(f"  - {file}")
            return False
        
        print("✅ All required files found")
        return True
    
    def install_dependencies(self):
        """Install required Python packages"""
        packages = [
            "fastapi",
            "uvicorn",
            "streamlit",
            "requests",
            "numpy",
            "scikit-learn",
            "sentence-transformers",
            "transformers",
            "torch",
            "faiss-cpu",
            "librosa",
            "pandas",
            "plotly"
        ]
        
        print("📦 Installing dependencies...")
        for package in packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"  ✅ {package}")
            except subprocess.CalledProcessError:
                print(f"  ❌ Failed to install {package}")
    
    def create_missing_files(self):
        """Create missing helper files if they don't exist"""
        
        # Create speech_to_text.py if missing
        if not Path("speech_to_text.py").exists():
            speech_to_text_content = '''
def transcribe_audio(audio_path: str) -> str:
    """Simple audio transcription fallback"""
    try:
        # This is a placeholder - in production you'd use Whisper or similar
        return "I am feeling emotional and need food recommendations"
    except Exception as e:
        print(f"Error in audio transcription: {e}")
        return "feeling emotional"
'''
            with open("speech_to_text.py", "w") as f:
                f.write(speech_to_text_content)
            print("✅ Created speech_to_text.py")
        
        # Create text_to_speech.py if missing
        if not Path("text_to_speech.py").exists():
            text_to_speech_content = '''
def convert_text_to_speech(text: str) -> bytes:
    """Simple text-to-speech fallback"""
    try:
        # This is a placeholder - in production you'd use TTS service
        return None
    except Exception as e:
        print(f"Error in text-to-speech: {e}")
        return None
'''
            with open("text_to_speech.py", "w") as f:
                f.write(text_to_speech_content)
            print("✅ Created text_to_speech.py")
        
        # Create sample meal.json if missing
        if not Path("meal.json").exists():
            sample_meals = [
                {
                    "meal_name": "Warm Chicken Soup",
                    "mood_1": "Sad",
                    "mood_2": "Tired",
                    "reason": "Comfort food that provides warmth and emotional comfort",
                    "benefit": "Rich in protein and vitamins, helps boost serotonin levels",
                    "calories": 250,
                    "cultural_theme": "Western Comfort",
                    "dietary_theme": "General"
                },
                {
                    "meal_name": "Green Tea and Dark Chocolate",
                    "mood_1": "Anxious",
                    "mood_2": "Restless",
                    "reason": "L-theanine in tea promotes calmness while chocolate releases endorphins",
                    "benefit": "Reduces cortisol levels and provides natural mood enhancement",
                    "calories": 150,
                    "cultural_theme": "Asian",
                    "dietary_theme": "Light"
                },
                {
                    "meal_name": "Quinoa Buddha Bowl",
                    "mood_1": "Tired",
                    "mood_2": "Foggy",
                    "reason": "Complex carbs and protein provide sustained energy",
                    "benefit": "B-vitamins support brain function and energy metabolism",
                    "calories": 420,
                    "cultural_theme": "Health-focused",
                    "dietary_theme": "Vegetarian"
                }
            ]
            
            import json
            with open("meal.json", "w") as f:
                json.dump(sample_meals, f, indent=2)
            print("✅ Created sample meal.json")
    
    def start_backend(self):
        """Start the FastAPI backend server"""
        try:
            print("🚀 Starting backend server...")
            self.backend_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", 
                "enhanced_backend:app", 
                "--host", "0.0.0.0", 
                "--port", "8000",
                "--reload"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            for i in range(30):  # Wait up to 30 seconds
                try:
                    response = requests.get(f"{self.backend_url}/health", timeout=1)
                    if response.status_code == 200:
                        print("✅ Backend server started successfully!")
                        print(f"   URL: {self.backend_url}")
                        return True
                except:
                    time.sleep(1)
            
            print("❌ Backend server failed to start")
            return False
            
        except Exception as e:
            print(f"❌ Error starting backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the Streamlit frontend"""
        try:
            print("🎨 Starting frontend server...")
            self.frontend_process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", 
                "enhanced_app.py",
                "--server.port", "8501",
                "--server.address", "0.0.0.0"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            time.sleep(3)  # Give Streamlit time to start
            print("✅ Frontend server started!")
            print(f"   URL: {self.frontend_url}")
            return True
            
        except Exception as e:
            print(f"❌ Error starting frontend: {e}")
            return False
    
    def stop_servers(self):
        """Stop both servers"""
        print("🛑 Stopping servers...")
        
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process.wait()
            print("✅ Backend stopped")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            self.frontend_process.wait()
            print("✅ Frontend stopped")
    
    def check_server_status(self):
        """Check if servers are running"""
        backend_status = "❌ Down"
        frontend_status = "❌ Down"
        
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=2)
            if response.status_code == 200:
                backend_status = "✅ Running"
        except:
            pass
        
        try:
            response = requests.get(self.frontend_url, timeout=2)
            if response.status_code == 200:
                frontend_status = "✅ Running"
        except:
            pass
        
        print(f"Backend ({self.backend_url}): {backend_status}")
        print(f"Frontend ({self.frontend_url}): {frontend_status}")
    
    def run_setup(self):
        """Run complete setup process"""
        print("🧠 AI Mood Meal Assistant - Setup")
        print("=" * 40)
        
        # Check dependencies
        if not self.check_dependencies():
            print("Please ensure all required files are in the current directory")
            return False
        
        # Install packages
        print("\n📦 Installing dependencies...")
        self.install_dependencies()
        
        # Create missing files
        print("\n📁 Creating missing helper files...")
        self.create_missing_files()
        
        print("\n✅ Setup complete!")
        return True
    
    def run_servers(self):
        """Start both servers"""
        print("🧠 AI Mood Meal Assistant - Starting Servers")
        print("=" * 50)
        
        # Start backend first
        if not self.start_backend():
            return False
        
        # Start frontend
        if not self.start_frontend():
            self.stop_servers()
            return False
        
        print("\n🎉 All servers started successfully!")
        print("\nAccess your application at:")
        print(f"  Frontend: {self.frontend_url}")
        print(f"  Backend API: {self.backend_url}")
        print(f"  API Docs: {self.backend_url}/docs")
        
        try:
            print("\nPress Ctrl+C to stop all servers...")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down servers...")
            self.stop_servers()
            print("👋 Goodbye!")
        
        return True

def main():
    """Main function"""
    manager = ServerManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "setup":
            manager.run_setup()
        elif command == "start":
            manager.run_servers()
        elif command == "stop":
            manager.stop_servers()
        elif command == "status":
            manager.check_server_status()
        elif command == "install":
            manager.install_dependencies()
        else:
            print("Available commands:")
            print("  setup  - Run initial setup")
            print("  start  - Start both servers")
            print("  stop   - Stop all servers")
            print("  status - Check server status")
            print("  install - Install dependencies only")
    else:
        # Interactive mode
        print("🧠 AI Mood Meal Assistant - Server Manager")
        print("=" * 45)
        print("1. Run setup (install dependencies & create files)")
        print("2. Start servers")
        print("3. Check server status")
        print("4. Stop servers")
        print("5. Exit")
        
        while True:
            try:
                choice = input("\nSelect option (1-5): ").strip()
                
                if choice == "1":
                    manager.run_setup()
                elif choice == "2":
                    manager.run_servers()
                    break
                elif choice == "3":
                    manager.check_server_status()
                elif choice == "4":
                    manager.stop_servers()
                elif choice == "5":
                    print("👋 Goodbye!")
                    break
                else:
                    print("Invalid choice. Please select 1-5.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break

if __name__ == "__main__":
    main()