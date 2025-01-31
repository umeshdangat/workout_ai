from fastapi import APIRouter
from backend.models.workouts import WorkoutPlan

router = APIRouter()

@router.get("/generate", response_model=WorkoutPlan)
def generate_workout():
    """
    Generates a sample workout dynamically.
    """
    sample_workout = WorkoutPlan(
        name="Full Body Strength",
        exercises=[
            {"name": "Squat", "sets": 4, "reps": 8, "intensity": "heavy"},
            {"name": "Bench Press", "sets": 4, "reps": 10, "intensity": "moderate"},
            {"name": "Deadlift", "sets": 3, "reps": 5, "intensity": "heavy"},
            {"name": "Pull-Ups", "sets": 3, "reps": 12, "intensity": "bodyweight"},
        ],
    )
    return sample_workout
