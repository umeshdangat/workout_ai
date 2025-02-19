from fastapi import APIRouter

from backend.api.search import router as search_router
from backend.api.workouts import router as workouts_router  # ✅ Import workouts router

router = APIRouter()
router.include_router(search_router, prefix="/workouts", tags=["workouts"])
router.include_router(workouts_router, prefix="/workouts", tags=["workouts"])
