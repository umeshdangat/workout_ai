from backend.models.workouts import WorkoutRequest
from backend.services.search import search_similar_workouts


def build_prompt(user_input: WorkoutRequest, week: int, previous_weeks_summary: str = "") -> str:
    """
    Builds a structured prompt for generating AI-driven workout programs with RAG.
    """

    # Retrieve similar workouts
    similar_workouts = search_similar_workouts(query=", ".join(user_input.goals), top_k=5)

    return f"""
    You are a highly experienced coach generating structured workout programs. Your task is to create a detailed workout plan in valid JSON format for {user_input.name}, a {user_input.age}-year-old {user_input.experience} athlete.

    Athlete Goals:
    - {', '.join(user_input.goals)}.

    Reference Workouts (Retrieved from Similar Programs):
    {similar_workouts}

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

