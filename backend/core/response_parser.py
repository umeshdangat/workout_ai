import json
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
)


def parse_openai_response_old(raw_json: str) -> WorkoutPlan:
    """
    Parse the raw JSON response from OpenAI into a structured `WorkoutPlan` object.
    """

    try:
        print(f"Parsing raw response...")
        # Parse JSON string into Python dictionary
        response_data = json.loads(raw_json)

        # Parse weeks
        weeks = []
        for week_data in response_data.get("weeks", []):
            days = []
            for day_data in week_data.get("days", []):
                sessions = []
                for session_data in day_data.get("sessions", []):
                    session_type = session_data.get("type", "").strip()
                    details = session_data.get("details", {})

                    if session_type == "WOD":
                        sessions.append(
                            Session(
                                type="WOD",
                                details=WOD(
                                    description=details.get("description", ""),
                                    intended_stimulus=details.get("intended_stimulus", ""),
                                    scaling_options=details.get("scaling_options", ""),
                                    movements=[
                                        Movement(
                                            description=movement.get("description", ""),
                                            resources=movement.get("resources", ""),
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
                                    description=details.get("description", ""),
                                    sets=details.get("sets", 0),
                                    reps=details.get("reps", 0),
                                    intensity=details.get("intensity", ""),
                                    rest=details.get("rest", ""),
                                    notes=details.get("notes", ""),
                                ),
                            )
                        )
                    elif session_type == "Rest Day":
                        rest_day = RestDay(
                            type="Rest Day",
                            description=details.get("description", "Take the day off to recover."),
                            notes=details.get("notes", "Take the day off to recover."),
                        )
                        sessions.append(Session(type="Rest Day", details=rest_day))
                    elif session_type == "Active Recovery":
                        sessions.append(
                            Session(
                                type="Active Recovery",
                                details=ActiveRecoveryDay(
                                    type="Active Recovery",
                                    description=details.get("description", "Recovery session"),
                                    activities=details.get("activities", []),
                                    duration=details.get("duration", "30-60 minutes"),
                                    intensity=details.get("intensity", "Low"),
                                ),
                            )
                        )
                    else:
                        print(f"⚠️ Unrecognized session type: {session_type}. Skipping.")

                days.append(Day(sessions=sessions))
            weeks.append(Week(days=days))

        print(f"✅ Workout plan parsed successfully for {len(weeks)} weeks.")
        return WorkoutPlan(name=response_data.get("name", "Generated Workout Plan"), weeks=weeks)

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        raise ValueError(f"Failed to parse OpenAI response: {str(e)}")
import json
from backend.models.workouts import WorkoutPlan, Week, Day, Session


def parse_openai_response(raw_json: str) -> WorkoutPlan:
    """Parse OpenAI's JSON response into a structured `WorkoutPlan`."""
    try:
        response_data = json.loads(raw_json)
        weeks = []

        for week_data in response_data.get("weeks", []):
            days = []
            for day_data in week_data.get("days", []):
                sessions = [Session.from_dict(session) for session in day_data.get("sessions", [])]
                days.append(Day(sessions=sessions))
            weeks.append(Week(days=days))

        return WorkoutPlan(name=response_data["name"], weeks=weeks)

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        raise ValueError(f"Failed to parse OpenAI response: {str(e)}")
