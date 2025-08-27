import streamlit as st

def save_dietary_preferences():
    """Component to save user dietary preferences"""
    st.markdown("### 🍽️ Dietary Preferences")
    
    dietary_restrictions = st.multiselect(
        "Select any dietary restrictions:",
        ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Nut-Free", "Low-Carb", "Keto", "Paleo"]
    )
    
    cultural_preferences = st.multiselect(
        "Preferred cuisines:",
        ["South Asian", "East Asian", "Mediterranean", "Middle Eastern", "Latin American", 
         "African", "Western Comfort", "Fusion"]
    )
    
    if st.button("Save Preferences"):
        st.session_state.preferences = {
            "dietary_restrictions": dietary_restrictions,
            "cultural_preferences": cultural_preferences
        }
        st.success("✅ Preferences saved successfully!")
