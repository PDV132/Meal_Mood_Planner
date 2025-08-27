import json

def load_meals(filepath="meal.json"):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
