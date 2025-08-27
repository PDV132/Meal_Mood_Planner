import streamlit as st
import requests

def check_server_health():
    """Check if the backend server is running and responding"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def save_dietary_preferences():
    st.markdown('<div class="preferences-box">', unsafe_allow_html=True)
    st.subheader("🍽️ Set Your Dietary Preferences")
    
    # Check if server is running
    if not check_server_health():
        st.error("⚠️ Backend server is not running. Please start the server and try again.")
        st.info("To start the server, run the backend application first.")
    
    # Dietary Restrictions
    restrictions = st.multiselect(
        "Select any dietary restrictions:",
        options=[
            "Vegetarian",
            "Vegan",
            "Gluten-Free",
            "Dairy-Free",
            "Kosher",
            "Halal",
            "None"
        ],
        default=[]
    )
    
    # Allergies
    allergies = st.multiselect(
        "Select any food allergies:",
        options=[
            "Peanuts",
            "Tree Nuts",
            "Milk",
            "Eggs",
            "Soy",
            "Fish",
            "Shellfish",
            "Wheat",
            "None"
        ],
        default=[]
    )
    
    # Preferred Cuisines
    cuisines = st.multiselect(
        "Select your preferred cuisines:",
        options=[
            "Italian",
            "Indian",
            "Chinese",
            "Japanese",
            "Mexican",
            "Mediterranean",
            "Thai",
            "American",
            "French"
        ],
        default=[]
    )
    
    # Disliked Ingredients
    disliked = st.text_area(
        "List ingredients you want to avoid (one per line):",
        help="Enter ingredients you want to avoid in your meals"
    )
    disliked_ingredients = [i.strip() for i in disliked.split('\n') if i.strip()]
    
    # Calorie Preference
    calories = st.number_input(
        "Daily calorie target (optional):",
        min_value=0,
        max_value=5000,
        value=2000,
        step=100
    )
    
    if st.button("Save Preferences"):
        try:
            preferences = {
                "user_id": "default_user",
                "dietary_preferences": {
                    "restrictions": restrictions,
                    "allergies": allergies,
                    "preferred_cuisines": cuisines,
                    "disliked_ingredients": disliked_ingredients,
                    "calories_target": calories if calories > 0 else None
                },
                "meal_tracking": {
                    "last_meal_time": None,
                    "next_meal_reminder": None,
                    "missed_meals_count": 0
                }
            }
            
            # First check if server is available
            if not check_server_health():
                st.error("⚠️ Backend server is not running. Please start the server and try again.")
                return False

            # Attempt to save preferences with increased timeout
            response = requests.post(
                "http://localhost:8000/api/user/preferences",
                json=preferences,
                timeout=10  # Increased timeout
            )
            
            if response.status_code == 200:
                st.success("✅ Preferences saved successfully!")
                st.balloons()
                # Store in session state to prevent re-execution
                st.session_state.preferences_saved = True
                return True
            
            st.error(f"Failed to save preferences. Server responded with status code: {response.status_code}")
            try:
                error_detail = response.json().get('detail', 'No additional details provided')
                st.error(f"Error details: {error_detail}")
            except:
                pass
            # Reset session state
            st.session_state.preferences_saved = False
            return False
                
        except requests.exceptions.ReadTimeout:
            st.error("⚠️ Server took too long to respond. The server might be busy or experiencing issues.")
            st.session_state.preferences_saved = False
            return False
        except requests.exceptions.ConnectionError:
            st.error("⚠️ Could not connect to the server. Please ensure the backend is running.")
            st.info("To start the server, run the backend application first.")
            st.session_state.preferences_saved = False
            return False
        except requests.exceptions.RequestException as e:
            st.error(f"⚠️ Error connecting to the server: {str(e)}")
            st.session_state.preferences_saved = False
            return False
        except Exception as e:
            st.error(f"⚠️ An unexpected error occurred: {str(e)}")
            st.session_state.preferences_saved = False
            return False
    
    st.markdown('</div>', unsafe_allow_html=True)
    return False
