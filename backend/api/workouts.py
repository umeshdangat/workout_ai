import json
import os
import time
from typing import Optional

import openai
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query
from backend.models.workouts import WorkoutPlan, WorkoutRequest, Exercise

# Initialize the router
router = APIRouter()

# Load environment variables
load_dotenv()

# Load OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API Key. Set OPENAI_API_KEY in .env or environment variables.")

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Constants for caching and rate limiting
CACHE_FILE = "openai_workout_cache.json"
MIN_TIME_BETWEEN_REQUESTS = 20  # in seconds
_last_request_time = 0  # Global variable to track the last request time


# ---------------------------------------------
# Utility Functions
# ---------------------------------------------

def save_to_cache(data: str, filename: str = CACHE_FILE) -> None:
    """Save raw OpenAI response to a cache file."""
    with open(filename, "w") as file:
        json.dump({"openai_response": data}, file, indent=4)


def load_from_cache(filename: str = CACHE_FILE) -> Optional[str]:
    """Load cached response from the cache file, if available."""
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return json.load(file).get("openai_response")
    return None


def clean_openai_response(raw_response: str) -> str:
    """Clean and sanitize the raw response from OpenAI."""
    # Remove Markdown formatting (if present)
    if raw_response.startswith("```json"):
        raw_response = raw_response.strip("```json").strip("```").strip()

    # Validate JSON
    try:
        json.loads(raw_response)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in OpenAI response: {raw_response}") from e

    return raw_response


def flatten_workout_data(raw_data: dict) -> list[Exercise]:
    """Flatten nested workout data into a list of Exercise objects."""
    exercises = []
    for week_index, week_data in enumerate(raw_data["exercises"], start=1):
        week_key = f"week {week_index}"
        if week_key in week_data:
            for exercise in week_data[week_key]:
                exercises.append(Exercise(
                    week=week_index,
                    name=exercise["exercise"],
                    sets=exercise["sets"],
                    reps=exercise["reps"],
                    intensity=exercise["intensity"]
                ))
    return exercises


# ---------------------------------------------
# Core Logic
# ---------------------------------------------

def parse_openai_response(raw_json: str) -> WorkoutPlan:
    """Parse OpenAI response into a WorkoutPlan."""
    # Clean the response
    raw_json = clean_openai_response(raw_json)

    # Convert JSON string to dictionary
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"❌ Invalid JSON format: {raw_json}") from e

    # Flatten workout data
    exercises = []
    for exercise in data.get("exercises", []):
        exercises.append(Exercise(
            week=exercise["week"],
            name=exercise["name"],
            sets=exercise["sets"],
            reps=exercise["reps"],
            intensity=exercise["intensity"]
        ))

    # Return the parsed workout plan
    return WorkoutPlan(name=data["name"], weeks=data["weeks"], exercises=exercises)


def generate_workout_with_ai(user_input: WorkoutRequest, force_generate: bool) -> WorkoutPlan:
    """Generate a workout plan using OpenAI GPT with caching and rate limiting."""
    global _last_request_time

    # Check cache
    if not force_generate:
        cached_response = load_from_cache()
        if cached_response:
            try:
                return parse_openai_response(cached_response)
            except ValueError:
                print("⚠ Cached response is invalid. Regenerating a new plan...")

    # Enforce rate limiting
    time_since_last_request = time.time() - _last_request_time
    if time_since_last_request < MIN_TIME_BETWEEN_REQUESTS:
        time.sleep(MIN_TIME_BETWEEN_REQUESTS - time_since_last_request)

    # Build the OpenAI prompt safely
    prompt = (
        f"Create a structured {user_input.weeks}-week workout plan for {user_input.name}, "
        f"a {user_input.age}-year-old {user_input.experience} lifter.\n"
        f"Goals: {', '.join(user_input.goals)}.\n"
        f"Available equipment: {', '.join(user_input.equipment)}.\n"
        f"Injuries: {', '.join(user_input.injuries) if user_input.injuries else 'None'}.\n"
        f"Avoid these exercises: {', '.join(user_input.avoid_exercises) if user_input.avoid_exercises else 'None'}.\n"
        "\nFormat the response as valid JSON with:\n"
        "- 'name': name of the plan\n"
        "- 'weeks': number of weeks\n"
        "- 'exercises': a list of workouts, structured like:\n"
        "  [\n"
        "      {\"week\": 1, \"name\": \"Back Squat\", \"sets\": 4, \"reps\": 6, \"intensity\": \"70% of 1RM\"},\n"
        "      {\"week\": 1, \"name\": \"Pull-Ups\", \"sets\": 3, \"reps\": 8, \"intensity\": \"Bodyweight\"}\n"
        "  ]"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[{"role": "system", "content": "You are a fitness coach generating structured training programs."},
                      {"role": "user", "content": prompt}],
            temperature=0.7,
        )

        _last_request_time = time.time()

        # Parse and save the response
        workout_text = response.choices[0].message.content.strip()
        save_to_cache(workout_text)
        return parse_openai_response(workout_text)

    except openai.RateLimitError as e:
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded: {str(e)}")
    except openai.OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")


# ---------------------------------------------
# API Endpoints
# ---------------------------------------------

@router.post("/generate", response_model=WorkoutPlan)
def generate_workout(request: WorkoutRequest, force_generate: bool = Query(False)):
    """
    API endpoint to generate a personalized training program.
    If `force_generate=True`, it makes a fresh API call; otherwise, it uses cached data.
    """
    return generate_workout_with_ai(request, force_generate)
