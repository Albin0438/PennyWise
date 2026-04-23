import json
import os

SETTINGS_FILE = "settings.json"

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {}

    with open(SETTINGS_FILE, "r") as file:
        return json.load(file)

def save_settings(data):
    with open(SETTINGS_FILE, "w") as file:
        json.dump(data, file)