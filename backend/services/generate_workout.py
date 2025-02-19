import os
from backend.core.openai_client import call_openai_api
from backend.core.cache import save_to_cache, load_from_cache
from backend.core.prompt_builder import build_prompt
from backend.core.response_parser import parse_openai_response
from backend.core.summary_genertor import summarize_week_for_next_prompt
from backend.models.workouts import WorkoutRequest, WorkoutPlan, Week

CACHE_DIR = "workout_cache"

def generate_weekly_workout(user_input: WorkoutRequest, week: int, previous_summary: str = "") -> Week:
    """
    Generate workouts for a specific week using OpenAI.
    """
    cache_file = os.path.join(CACHE_DIR, f"week_{week}.json")

    # Load from cache if available
    cached_response = load_from_cache(cache_file)
    if cached_response:
        print(f"📂 Using cached response from {cache_file}")
        return parse_openai_response(cached_response).weeks[0]

    # Call OpenAI API
    prompt = build_prompt(user_input, week, previous_summary)
    print("📡 No cached response available. Fetching workouts from tracks from OpenAI...")
    workout_text = call_openai_api(prompt)

    # Save to cache
    print(f"✅ Fetched workouts from OpenAI. Saving to {cache_file}...")
    save_to_cache(workout_text, cache_file)

    return parse_openai_response(workout_text).weeks[0]

def generate_workout_with_ai(user_input: WorkoutRequest) -> WorkoutPlan:
    """
    Generate a full workout plan for the requested duration.
    """
    weeks = []
    previous_summary = ""

    for week in range(1, user_input.duration + 1):
        week_plan = generate_weekly_workout(user_input, week, previous_summary)
        weeks.append(week_plan)
        previous_summary = summarize_week_for_next_prompt(week_plan)

    return WorkoutPlan(name=f"{user_input.name}'s Plan", weeks=weeks)
