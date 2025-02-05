import json
import os
import time
from typing import Optional

import openai
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException

from backend.models.workouts import (
    WorkoutPlan,
    Week,
    Day,
    Session,
    WOD,
    Strength,
    RestDay,
    ActiveRecoveryDay,
    Movement,
    WorkoutRequest,
)

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
CACHE_DIR = "workout_cache"  # Directory to store weekly cache files
MIN_TIME_BETWEEN_REQUESTS = 20  # in seconds
_last_request_time = 0  # Global variable to track the last request time

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)


# ---------------------------------------------
# Utility Functions
# ---------------------------------------------

def save_to_cache(data: str, filename: str) -> None:
    """Save raw OpenAI response to a cache file."""
    with open(filename, "w") as file:
        json.dump({"openai_response": data}, file, indent=4)


def load_from_cache(filename: str) -> Optional[str]:
    """Load cached response from a cache file, if available."""
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return json.load(file).get("openai_response")
    return None


def parse_openai_response(raw_json: str) -> WorkoutPlan:
    """
    Parse the raw JSON response from OpenAI into a structured WorkoutPlan.
    """
    try:
        # Parse JSON string into Python dictionary
        response_data = json.loads(raw_json)

        # Parse weeks
        weeks = []
        for week_data in response_data.get("weeks", []):
            days = []
            for day_data in week_data.get("days", []):
                sessions = []
                for session_data in day_data.get("sessions", []):
                    session_type = session_data.get("type")
                    details = session_data.get("details")

                    if session_type == "WOD":
                        sessions.append(
                            Session(
                                type="WOD",
                                details=WOD(
                                    description=details.get("description"),
                                    intended_stimulus=details.get("intended_stimulus"),
                                    scaling_options=details.get("scaling_options"),
                                    movements=[
                                        Movement(
                                            description=movement.get("description"),
                                            resources=movement.get("resources"),
                                        )
                                        for movement in details.get("movements", [])
                                    ],
                                ),
                            )
                        )
                    elif session_type == "Strength":
                        sessions.append(
                            Session(
                                type="Strength",
                                details=Strength(
                                    description=details.get("description"),
                                    sets=details.get("sets"),
                                    reps=details.get("reps"),
                                    intensity=details.get("intensity"),
                                    rest=details.get("rest"),
                                    notes=details.get("notes"),
                                ),
                            )
                        )
                    elif session_type == "RestDay":
                        sessions.append(Session(type="Rest Day", details=RestDay(
                            notes=session_data["details"].get("notes", "Take the day off to recover.")
                        )))
                    elif session_type == "Active Recovery":
                        sessions.append(Session(type="Active Recovery", details=ActiveRecoveryDay(
                            activities=details.get("activities", []),
                            duration=details.get("duration", "30-60 minutes"),
                            intensity=details.get("intensity", "Low"),
                        )))

                days.append(Day(sessions=sessions))
            weeks.append(Week(days=days))

        return WorkoutPlan(name=response_data["name"], weeks=weeks)

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        raise ValueError(f"Failed to parse OpenAI response: {str(e)}")


# ---------------------------------------------
# Core Logic
# ---------------------------------------------

def build_prompt(user_input: WorkoutRequest, week: int) -> str:
    """Builds the prompt for the OpenAI API call."""
    return f"""
    You are a coach generating structured workout programs. Your task is to create a structured JSON workout plan for {user_input.name}, a {user_input.age}-year-old {user_input.experience} athlete.

    Details:
    - Goals: {', '.join(user_input.goals)}.
    - Avoid repeating benchmark CrossFit WODs. Create new, custom workouts. Mention the workout details in the description field.
    - Available equipment: {', '.join(user_input.equipment)}.
    - Injuries: {', '.join(user_input.injuries) if user_input.injuries else 'None'}.
    - Avoid exercises: {', '.join(user_input.avoid_exercises) if user_input.avoid_exercises else 'None'}.
    - Sessions per week: {user_input.sessions_per_week}.
    - Session duration: {user_input.constraints or '75-90 minutes'}.

    Output Requirements:
    - Strictly adhere to the following JSON schema.
    - Do not wrap the response in Markdown or as a string.
    - Return a valid JSON object.

    Schema:
    {{
        "name": "Program Name",
        "weeks": [
            {{
                "days": [
                    {{
                        "sessions": [
                            {{
                                "type": "WOD",
                                "details": {{
                                    "description": "Fran: 21-15-9 reps of thrusters(95#/65#) and pull-ups",
                                    "intended_stimulus": "Quick and intense",
                                    "scaling_options": "Reduce weight if needed, aim for unbroken sets",
                                    "movements": [
                                        {{
                                            "description": "Thrusters (95/65 lbs)",
                                            "resources": "https://link.to/movement"
                                        }},
                                        {{
                                            "description": "Pull-ups",
                                            "resources": "https://link.to/movement"
                                        }}
                                    ]
                                }}
                            }},
                            {{
                                "type": "Strength",
                                "details": {{
                                    "description": "Push Press escalating load from 70% to 85% of 1RM",
                                    "sets": 5,
                                    "reps": 3,
                                    "intensity": "85% of 1RM",
                                    "rest": "2 minutes between sets",
                                    "notes": "Focus on technique and speed"
                                }}
                            }},
                            {{
                                "type": "Rest Day",
                                "details": {{
                                    "notes": "Take the day off to recover.",
                                    "description": "An apple a day keeps the doctor away! Eat well"
                                }}
                            }},
                            {{
                                "type": "Active Recovery",
                                "details": {{
                                    "activities": ["Mobility work", "Foam rolling"],
                                    "duration": "30-60 minutes",
                                    "intensity": "Low",
                                    "description": "Take a stroll in the park"
                                }}
                            }}
                        ]
                    }}
                ]
            }}
        ]
    }}

    Generate a workout plan for week {week}. Ensure the output is valid JSON, adheres to the schema, and is not wrapped in Markdown or as a string.
    """


def generate_weekly_workout(user_input: WorkoutRequest, week: int) -> Week:
    """
    Generate workout sessions for a specific week.
    """
    global _last_request_time

    # Cache file for the specific week
    cache_file = os.path.join(CACHE_DIR, f"week_{week}.json")

    # Load from cache if available
    cached_response = load_from_cache(cache_file)
    if cached_response:
        print(f"Cached raw response for week: {week} present, Reloading from cache...")
        try:
            print(f"parsing raw response for week {week}...")
            return parse_openai_response(cached_response).weeks[0]
        except ValueError:
            print(f"⚠ Cached response for week {week} is invalid. Regenerating...")

    # Enforce rate limiting
    time_since_last_request = time.time() - _last_request_time
    if time_since_last_request < MIN_TIME_BETWEEN_REQUESTS:
        print(
            f"time_since_last_request less than {time_since_last_request}. "
            f"Enforcing rate limiting by throttling for {MIN_TIME_BETWEEN_REQUESTS - time_since_last_request} seconds...")
        time.sleep(MIN_TIME_BETWEEN_REQUESTS - time_since_last_request)

    # Prompt to guide OpenAI API
    prompt = build_prompt(user_input, week)
    print(f"prompt: {prompt}")
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a fitness coach generating structured training programs."},
                      {"role": "user", "content": prompt}],
            temperature=0.7,
        )

        _last_request_time = time.time()

        # Save and parse the response
        workout_text = response.choices[0].message.content.strip()
        print(f"saving raw response for week {week}... to cache_file: {cache_file}")
        save_to_cache(workout_text, cache_file)
        try:
            print(f"parsing raw response for week {week}...")
            response = parse_openai_response(workout_text).weeks[0]
        except Exception as e:
            raise ValueError(f"Failed to parse OpenAI response: {str(e)}")
        return response

    except openai.OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")


def generate_workout_with_ai(user_input: WorkoutRequest) -> WorkoutPlan:
    """
    Generate a full workout plan for the requested duration.
    """
    weeks = [generate_weekly_workout(user_input, week) for week in range(1, user_input.duration + 1)]
    return WorkoutPlan(name=f"{user_input.name}'s Plan", weeks=weeks)


# ---------------------------------------------
# API Endpoints
# ---------------------------------------------

@router.post("/generate", response_model=WorkoutPlan)
def generate_workout(request: WorkoutRequest):
    """
    API endpoint to generate a workout plan.
    """
    return generate_workout_with_ai(request)
