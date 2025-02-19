def get_workout_category(workout):
    """
    Classifies workouts as warmup, cooldown, or main workout.
    """
    title = workout["title"].lower().strip()
    score_type = workout["score_type"].strip().lower()

    if any(kw in title for kw in ["pre-wod", "warmup", "mobility"]):
        return "warmup"
    elif any(kw in title for kw in ["cooldown", "recovery", "stretch"]):
        return "cooldown"
    elif score_type:
        return "workout"
    return "other"
