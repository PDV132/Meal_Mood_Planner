import streamlit as st

def get_dietary_preferences():
    """
    Display and handle dietary preferences form
    """
    st.subheader("🍽️ Dietary Preferences")
    
    with st.expander("Set Your Dietary Preferences", expanded=True):
        # Dietary Restrictions
        st.write("### Dietary Restrictions")
        dietary_restrictions = st.multiselect(
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
        st.write("### Allergies")
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
        st.write("### Preferred Cuisines")
        preferred_cuisines = st.multiselect(
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
        disliked_ingredients = st.text_area(
            "List any ingredients you dislike (one per line):",
            help="Enter ingredients you want to avoid"
        ).split('\n')
        disliked_ingredients = [i.strip() for i in disliked_ingredients if i.strip()]
        
        # Calorie Preference
        calorie_target = st.number_input(
            "Daily Calorie Target (optional):",
            min_value=0,
            max_value=5000,
            value=2000,
            step=100,
            help="Set your daily calorie target"
        )
        
        # Save Button
        if st.button("Save Preferences"):
            preferences = {
                "dietary_preferences": {
                    "restrictions": dietary_restrictions,
                    "allergies": allergies,
                    "preferred_cuisines": preferred_cuisines,
                    "disliked_ingredients": disliked_ingredients,
                    "calories_target": calorie_target if calorie_target > 0 else None
                }
            }
            return preferences
            
    return None
