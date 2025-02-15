import json
import os

CACHE_DIR = "workout_cache"
os.makedirs(CACHE_DIR, exist_ok=True)


def save_to_cache(data: str, filename: str) -> None:
    """Save OpenAI response to cache."""
    with open(filename, "w") as file:
        json.dump({"openai_response": data}, file, indent=4)


def load_from_cache(filename: str) -> str:
    """Load cached OpenAI response if available."""
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return json.load(file).get("openai_response")
    return None
