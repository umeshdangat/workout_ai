from pydantic import BaseModel
from typing import List, Dict, Optional

class Exercise(BaseModel):
    week: int  # Add week field for easier lookup
    name: str
    sets: int
    reps: int
    intensity: str  # e.g., "light", "moderate", "heavy"

class WorkoutPlan(BaseModel):
    name: str
    weeks: int
    exercises: List[Exercise]  # Ensure a flat list

class WorkoutRequest(BaseModel):
    name: str
    age: int
    experience: str  # "beginner", "intermediate", "advanced"
    goals: List[str]  # e.g., ["increase PR", "Olympic lifting", "hypertrophy"]
    equipment: List[str]  # e.g., ["barbell", "dumbbells", "pull-up bar"]
    weeks: int  # Length of training plan
    injuries: Optional[List[str]] = []  # e.g., ["knee", "shoulder"]
    avoid_exercises: Optional[List[str]] = []  # e.g., ["deadlifts", "snatch"]
