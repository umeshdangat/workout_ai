from typing import List, Optional, Union

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
# Core Models
# ------------------------
class Movement(BaseModel):
    description: str  # Description of the movement
    resources: Optional[str] = None  # Link to tutorial or demo (e.g., "https://www.crossfit.com/movement")


class WOD(BaseModel):
    description: str  # Details of the WOD (e.g., workout structure)
    intended_stimulus: str  # Goals of the workout (e.g., "fast-paced, unbroken")
    scaling_options: str  # How athletes can scale the workout
    movements: List[Movement]  # List of movements with descriptions and resources


class Strength(BaseModel):
    description: str
    sets: Optional[str] = None  # Number of sets
    reps: Optional[str] = None # Number of reps
    intensity: Optional[str] = None  # Intensity level (e.g., "70% of 1RM")
    rest: Optional[str] = None  # Rest time between sets (e.g., "2 minutes")
    notes: Optional[str] = None  # Additional notes for guidance

class RestDay(BaseModel):
    type: str = "Rest Day"
    description: Optional[str] = "Take the day off to recover."
    notes: Optional[str] = "Take the day off to recover."

class ActiveRecoveryDay(BaseModel):
    type: str = "Active Recovery"
    description: Optional[str] = None
    activities: Optional[List[str]] = ["Mobility work", "Light cardio", "Foam rolling"]
    duration: Optional[str] = "30-60 minutes"
    intensity: Optional[str] = "Low"

# ------------------------
# Session Model
# ------------------------
class Session(BaseModel):
    type: str  # "WOD", "Strength", "Rest Day", "Active Recovery"
    details: Optional[Union[WOD, Strength, RestDay, ActiveRecoveryDay]]


# ------------------------
# Daily Structure
# ------------------------
class Day(BaseModel):
    sessions: List[Session] # A list of sessions for this day (can include WOD, Strength, or Recovery)


# ------------------------
# Weekly Structure
# ------------------------
class Week(BaseModel):
    days: List[Day]  # List of days in the week


# ------------------------
# Plan Model
# ------------------------
class WorkoutPlan(BaseModel):
    name: str  # Name of the workout plan
    weeks: List[Week]  # List of weeks in the plan
