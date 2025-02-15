import json
import os
import time
from typing import Optional

import faiss
import openai
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query

from backend.core.create_embeddings import model
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

# Load INDEX_DIR from .env
load_dotenv()
INDEX_DIR = os.getenv("FAISS_INDEX_DIR")

# Paths for FAISS Index & Metadata
FAISS_INDEX_PATH = f"{INDEX_DIR}/workout_embeddings.index"
METADATA_PATH = f"{INDEX_DIR}/workout_metadata.json"

# Load FAISS index
try:
    index = faiss.read_index(FAISS_INDEX_PATH)
except Exception as e:
    raise RuntimeError(f"Failed to load FAISS index: {str(e)}")

# Load metadata
try:
    with open(METADATA_PATH, "r") as f:
        workout_metadata = json.load(f)
except Exception as e:
    raise RuntimeError(f"Failed to load metadata JSON: {str(e)}")

# FastAPI Router
router = APIRouter()

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

def build_prompt(user_input: WorkoutRequest, week: int, previous_weeks_summary: Optional[str] = "") -> str:
    """Builds an improved prompt for the OpenAI API call."""
    return f"""
    You are a highly experienced coach generating structured workout programs. Your task is to create a detailed workout plan in valid JSON format for {user_input.name}, a {user_input.age}-year-old {user_input.experience} athlete.

    Athlete Goals:
    - {', '.join(user_input.goals)}.

    Training Guidelines:
    - Avoid repeating benchmark CrossFit WODs like "Grace" or "Fran" multiple times in the program. Create new, custom workouts with unique names.
    - Incorporate progressive overload for strength training and Olympic lifts (e.g., increasing weight, volume, or intensity weekly).
    - Include CrossFit WODs with high-skill movements (e.g., handstand push-ups, double-unders, bar muscle-ups).
    - Ensure a balance between WODs, strength sessions, and recovery days to avoid overtraining or burnout.
    - Use the following athlete details to customize the plan:
        - Available equipment: {', '.join(user_input.equipment)}.
        - Injuries: {', '.join(user_input.injuries) if user_input.injuries else 'None'}.
        - Avoid these exercises: {', '.join(user_input.avoid_exercises) if user_input.avoid_exercises else 'None'}.
        - Sessions per week: {user_input.sessions_per_week}.
        - Session duration: {user_input.constraints or '75-90 minutes'}.

    Program Continuity:
    - Reference the following summary of previous weeks' performance and structure to ensure continuity and progression:
      {previous_weeks_summary or "No data from previous weeks provided. Start with baseline workouts for week 1."}
    - Apply progressive overload principles:
      - Increase load, volume, or intensity for strength training sessions week-to-week.
      - Introduce progressively harder WODs or higher-skill movements as the athlete progresses.

    Output Requirements:
    - Return **only** a valid JSON object. Do not include any markdown formatting, such as ```json.
    - The response must strictly adhere to the following JSON schema:

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
                                    "description": "Custom WOD description (e.g., Fran: 21-15-9 reps of thrusters and pull-ups)",
                                    "intended_stimulus": "Stimulus goal (e.g., Quick and intense, focus on unbroken sets)",
                                    "scaling_options": "Scaling guidance (e.g., Reduce weight to maintain intensity)",
                                    "movements": [
                                        {{
                                            "description": "Thrusters (95/65 lbs)",
                                            "resources": "https://link.to/thrusters"
                                        }},
                                        {{
                                            "description": "Pull-ups",
                                            "resources": "https://link.to/pullups"
                                        }}
                                    ]
                                }}
                            }},
                            {{
                                "type": "Strength",
                                "details": {{
                                    "description": "Strength session description (e.g., Back Squat 5x5 at 80% of 1RM)",
                                    "sets": 5,
                                    "reps": 3,
                                    "intensity": "Intensity details (e.g., 80% of 1RM)",
                                    "rest": "Rest period between sets (e.g., 2-3 minutes)",
                                    "notes": "Execution notes (e.g., Focus on depth and explosive drive)"
                                }}
                            }},
                            {{
                                "type": "Rest Day",
                                "details": {{
                                    "notes": "Rest guidance (e.g., Take the day off to recover.)",
                                    "description": "Rest day notes (e.g., An apple a day keeps the doctor away! Eat well)"
                                }}
                            }},
                            {{
                                "type": "Active Recovery",
                                "details": {{
                                    "activities": ["Mobility work", "Foam rolling"],
                                    "duration": "Duration of recovery session (e.g., 30-60 minutes)",
                                    "intensity": "Recovery intensity (e.g., Low)",
                                    "description": "Description of recovery focus (e.g., Take a stroll in the park)"
                                }}
                            }}
                        ]
                    }}
                ]
            }}
        ]
    }}

    Generate a workout plan for week {week}. Ensure the output is valid JSON, adheres to the schema, and reflects the athlete's goals and training guidelines. Do not include any extraneous text or formatting outside of the JSON object.
    """


def summarize_week_for_next_prompt(week: Week) -> str:
    """
    Summarize the week's workouts for continuity in the next prompt.
    """
    summary = []
    for day_idx, day in enumerate(week.days, start=1):
        day_summary = f"Day {day_idx}:"
        for session in day.sessions:
            if session.type == "WOD":
                wod_details = session.details
                day_summary += (
                    f" WOD - {wod_details.description} | Stimulus: {wod_details.intended_stimulus};"
                )
            elif session.type == "Strength":
                strength_details = session.details
                day_summary += (
                    f" Strength - {strength_details.description}, {strength_details.sets}x{strength_details.reps} "
                    f"at {strength_details.intensity} | Notes: {strength_details.notes};"
                )
            elif session.type == "Rest Day":
                rest_details = session.details
                day_summary += f" Rest Day - {getattr(rest_details, 'description', 'Rest and recover.')};"
            elif session.type == "Active Recovery":
                recovery_details = session.details
                day_summary += (
                    f" Active Recovery - {getattr(recovery_details, 'description', 'Recovery session')}, "
                    f"Duration: {getattr(recovery_details, 'duration', '30-60 minutes')};"
                )
        summary.append(day_summary)
    return " ".join(summary)


def generate_weekly_workout(user_input: WorkoutRequest, week: int, previous_weeks_summary: str = "") -> Week:
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
    prompt = build_prompt(user_input, week, previous_weeks_summary)
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
    weeks = []
    previous_weeks_summary = ""
    for week in range(1, user_input.duration + 1):
        # Generate the week's workout plan
        week_plan = generate_weekly_workout(user_input, week, previous_weeks_summary)
        # Add the week to the plan
        weeks.append(week_plan)
        # Update the summary for the next week's prompt
        previous_weeks_summary = summarize_week_for_next_prompt(week_plan)

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


def get_workout_category(workout):
    """
    Classify workout category based on title and score type.
    """
    title = workout["title"].lower().strip()
    score_type = workout["score_type"].strip().lower()

    # Warmups typically have common identifiers
    if any(kw in title for kw in ["pre-wod", "warmup", "mobility"]):
        return "warmup"
    elif any(kw in title for kw in ["cooldown", "recovery", "stretch"]):
        return "cooldown"
    elif score_type:  # If there's a score, it's likely a main workout
        return "workout"
    return "other"


@router.get("/search_similar_workouts")
def search_similar_workouts(
        query: str = Query(..., description="Search query for workouts"),
        top_k: int = 10,
        include_warmups: bool = Query(True, description="Include warmups"),
        include_cooldowns: bool = Query(True, description="Include cooldowns"),
):
    """
    Search for similar workouts using FAISS text embeddings.
    Filters results by warmups, cooldowns, or main workouts.
    """
    query_embedding = model.encode([query], convert_to_numpy=True)

    # Ensure correct dimensions
    if query_embedding.shape[1] != index.d:
        raise HTTPException(status_code=400,
                            detail=f"Query embedding size mismatch: {query_embedding.shape[1]} != {index.d}")

    distances, indices = index.search(query_embedding, top_k)

    results, warmups, cooldowns = [], [], []

    for i, idx in enumerate(indices[0]):
        if idx < len(workout_metadata):
            workout = workout_metadata[idx]
            workout_category = get_workout_category(workout)

            result = {
                "rank": i + 1,
                "title": workout["title"],
                "description": workout["description"],
                "score_type": workout["score_type"],
                "workout_type": workout["workout_type"],
                "track": workout["track"],
                "created_at": workout["created_at"],
                "distance": float(distances[0][i]),  # Lower is better
            }

            # Categorize
            if workout_category == "warmup" and include_warmups:
                warmups.append(result)
            elif workout_category == "cooldown" and include_cooldowns:
                cooldowns.append(result)
            else:
                results.append(result)

    return {
        "query": query,
        "results": results,
        "warmups": warmups,
        "cooldowns": cooldowns
    }
