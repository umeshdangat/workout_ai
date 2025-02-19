from typing import List, Optional, Dict, Type
from typing import Union

from pydantic import BaseModel


# ------------------------
# Request Model
# ------------------------
class WorkoutRequest(BaseModel):
    name: str  # Name of the person requesting the plan
    age: int  # Age of the user
    experience: str  # Experience level (e.g., "beginner", "intermediate", "advanced")
    goals: List[str]  # List of goals (e.g., "increase PR", "improve handstands", "build endurance")
    equipment: List[str]  # List of available equipment (e.g., "barbell", "pull-up bar", "dumbbells")
    injuries: Optional[List[str]] = None  # List of injuries to consider (e.g., "knee", "shoulder")
    avoid_exercises: Optional[List[str]] = None  # Exercises to avoid
    sessions_per_week: Optional[int] = 6  # Number of training sessions per week
    training_preferences: Optional[
        List[str]
    ] = None  # Specific session types or modalities (e.g., "CrossFit", "skill work", "Olympic lifting")
    constraints: Optional[
        List[str]
    ] = None  # Additional constraints (e.g., "morning workouts only", "45-minute sessions")
    duration: Optional[int] = 8  # Total program duration in weeks
    recovery_days: Optional[int] = None  # Number of active recovery days per week

# ------------------------
# Base Class for Sessions
# ------------------------
class SessionDetails(BaseModel):
    """Base class for all session types."""
    @classmethod
    def from_dict(cls, type: str, details: Dict) -> "SessionDetails":
        """Factory method to create the correct session type."""
        session_classes: Dict[str, Type["SessionDetails"]] = {
            "WOD": WOD,
            "Strength": Strength,
            "Rest Day": RestDay,
            "Active Recovery": ActiveRecoveryDay
        }
        session_cls = session_classes.get(type)
        if session_cls:
            return session_cls(**details)
        raise ValueError(f"Unknown session type: {type}")



# ------------------------
# Core Models (Inherit from SessionDetails)
# ------------------------

class Movement(BaseModel):
    description: str
    resources: Optional[str] = None


class WOD(SessionDetails):
    description: str
    intended_stimulus: str
    scaling_options: str
    movements: List[Movement]


class Strength(SessionDetails):
    description: str
    sets: Optional[int] = None
    reps: Optional[int] = None
    intensity: Optional[str] = None
    rest: Optional[str] = None
    notes: Optional[str] = None


class RestDay(SessionDetails):
    type: str = "Rest Day"
    description: Optional[str] = "Take the day off to recover."
    notes: Optional[str] = "Take the day off to recover."


class ActiveRecoveryDay(SessionDetails):
    type: str = "Active Recovery"
    description: Optional[str] = None
    activities: Optional[List[str]] = ["Mobility work", "Light cardio", "Foam rolling"]
    duration: Optional[str] = "30-60 minutes"
    intensity: Optional[str] = "Low"


# ------------------------
# Session Model
# ------------------------

class Session(BaseModel):
    type: str
    details: SessionDetails

    @classmethod
    def from_dict(cls, session_data: Dict) -> "Session":
        """Factory method to create a session with the correct `details` type."""
        session_type = session_data["type"]
        details = SessionDetails.from_dict(session_type, session_data["details"])
        return cls(type=session_type, details=details)


# ------------------------
# Daily, Weekly, and Plan Models
# ------------------------

class Day(BaseModel):
    sessions: List[Session]


class Week(BaseModel):
    days: List[Day]


class WorkoutPlan(BaseModel):
    name: str
    weeks: List[Week]