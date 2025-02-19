from backend.models.workouts import Week


def summarize_week_for_next_prompt(week: Week) -> str:
    """
    Summarize the week's workouts for continuity in the next prompt.

    Args:
        week (Week): The workout plan for the current week.

    Returns:
        str: A text summary of the week's workouts.
    """
    summary = []
    for day_idx, day in enumerate(week.days, start=1):
        day_summary = f"Day {day_idx}:"
        for session in day.sessions:
            if session.type == "WOD":
                wod_details = session.details
                day_summary += (
                    f" WOD - {wod_details.description} | "
                    f"Stimulus: {wod_details.intended_stimulus};"
                )
            elif session.type == "Strength":
                strength_details = session.details
                day_summary += (
                    f" Strength - {strength_details.description}, "
                    f"{strength_details.sets}x{strength_details.reps} "
                    f"at {strength_details.intensity} | Notes: {strength_details.notes};"
                )
            elif session.type == "Rest Day":
                day_summary += " Rest Day - Recovery & Rest."
            elif session.type == "Active Recovery":
                recovery_details = session.details
                day_summary += (
                    f" Active Recovery - {', '.join(recovery_details.activities)}, "
                    f"Duration: {recovery_details.duration};"
                )
        summary.append(day_summary)

    return " ".join(summary)
