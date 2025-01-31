from pydantic import BaseModel
from typing import List, Dict

class WorkoutPlan(BaseModel):
    name: str
    exercises: List[Dict[str, str | int]]
