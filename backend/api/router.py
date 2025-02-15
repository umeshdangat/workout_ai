from fastapi import APIRouter

from backend.api.search import router as search_router

router = APIRouter()
router.include_router(search_router, prefix="/workouts", tags=["workouts"])
