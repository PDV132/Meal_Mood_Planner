import json
from datetime import datetime

LOG_PATH = "meal_log.json"

def log_meal(user: str, meal: str):
    try:
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    data[user] = {"meal": meal, "timestamp": datetime.utcnow().isoformat()}

    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def get_last_meal(user: str):
    try:
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
        return data.get(user)
    except (FileNotFoundError, json.JSONDecodeError):
        return None