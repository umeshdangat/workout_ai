from fastapi import FastAPI
from backend.api.workouts import router as workout_router

app = FastAPI(
    title="WorkoutAI API",
    description="AI-Powered Adaptive Strength & HIIT Training API",
    version="0.1.0"
)

# Health Check Endpoint
@app.get("/")
def read_root():
    return {"message": "WorkoutAI API is running!"}

# Include Workout Endpoints
app.include_router(workout_router, prefix="/workouts", tags=["Workouts"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
# FastAPI entrypoint
