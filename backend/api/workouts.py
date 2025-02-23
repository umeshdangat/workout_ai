from fastapi import APIRouter, HTTPException
from backend.models.workouts import WorkoutPlan, WorkoutPlanPydantic, WorkoutRequest
from backend.services.generate_workout import generate_workout_with_ai

router = APIRouter()

@router.post("/generate", response_model=WorkoutPlanPydantic)
def generate_workout(request: WorkoutRequest):
    """
    API endpoint to generate a workout plan using AI.
    """
    try:
        plan = generate_workout_with_ai(request)
        return plan.to_pydantic()  # ✅ Convert dataclass to Pydantic before returning
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
