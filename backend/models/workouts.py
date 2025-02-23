from typing import List, Optional, Dict, Type
from dataclasses import dataclass, field


# ------------------------
# Request Model (Pydantic Stays Here)
# ------------------------
from pydantic import BaseModel

class WorkoutRequest(BaseModel):
    name: str
    age: int
    experience: str
    goals: List[str]
    equipment: List[str]
    injuries: Optional[List[str]] = None
    avoid_exercises: Optional[List[str]] = None
    sessions_per_week: Optional[int] = 6
    training_preferences: Optional[List[str]] = None
    constraints: Optional[List[str]] = None
    duration: Optional[int] = 8
    recovery_days: Optional[int] = None


# ------------------------
# Internal Models (Dataclasses)
# ------------------------

@dataclass
class Movement:
    description: str
    resources: Optional[str] = None


@dataclass
class WOD:
    session_type: str = "WOD"
    description: str = ""
    intended_stimulus: str = ""
    scaling_options: str = ""
    movements: List[Movement] = field(default_factory=list)


@dataclass
class Strength:
    session_type: str = "Strength"
    description: str = ""
    sets: Optional[int] = None
    reps: Optional[int] = None
    intensity: Optional[str] = None
    rest: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class RestDay:
    session_type: str = "Rest Day"
    description: Optional[str] = "Take the day off to recover."
    notes: Optional[str] = "Take the day off to recover."


@dataclass
class ActiveRecoveryDay:
    session_type: str = "Active Recovery"
    description: Optional[str] = None
    activities: List[str] = field(default_factory=lambda: ["Mobility work", "Light cardio", "Foam rolling"])
    duration: str = "30-60 minutes"
    intensity: str = "Low"


@dataclass
class Session:
    type: str
    details: object  # 🔹 This avoids incorrect Pydantic parsing issues

    @classmethod
    def from_dict(cls, session_data: Dict) -> "Session":
        """Factory method to create a session with the correct `details` type."""
        session_classes: Dict[str, Type] = {
            "WOD": WOD,
            "Strength": Strength,
            "Rest Day": RestDay,
            "Active Recovery": ActiveRecoveryDay
        }
        session_type = session_data["type"]
        session_cls = session_classes.get(session_type, None)

        if not session_cls:
            raise ValueError(f"Unknown session type: {session_type}")

        details = session_cls(**session_data["details"])  # ✅ No Pydantic conversion issues
        return cls(type=session_type, details=details)


@dataclass
class Day:
    sessions: List[Session] = field(default_factory=list)


@dataclass
class Week:
    days: List[Day] = field(default_factory=list)


@dataclass
class WorkoutPlan:
    name: str
    weeks: List[Week] = field(default_factory=list)

    def to_pydantic(self):
        """Convert internal dataclass model to Pydantic model for FastAPI response."""
        return WorkoutPlanPydantic(
            name=self.name,
            weeks=[WeekPydantic(days=[
                DayPydantic(sessions=[
                    SessionPydantic(type=s.type, details=s.details.__dict__) for s in d.sessions
                ]) for d in w.days
            ]) for w in self.weeks]
        )


# ------------------------
# Pydantic Models for API Response
# ------------------------
class SessionPydantic(BaseModel):
    type: str
    details: Dict  # ✅ No serialization issues

class DayPydantic(BaseModel):
    sessions: List[SessionPydantic]

class WeekPydantic(BaseModel):
    days: List[DayPydantic]

class WorkoutPlanPydantic(BaseModel):
    name: str
    weeks: List[WeekPydantic]

