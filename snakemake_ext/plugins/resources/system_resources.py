import json

def load_system_resources(filepath):
    with open(filepath, "r") as f:
        return json.load(f)