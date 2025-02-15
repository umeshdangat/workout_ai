from fastapi import APIRouter, HTTPException, Query

from backend.services.search import search_similar_workouts

router = APIRouter()


@router.get("/search_similar_workouts")
def search(
        query: str = Query(..., description="Search query for workouts"),
        top_k: int = 10,
        include_warmups: bool = Query(True, description="Include warmups"),
        include_cooldowns: bool = Query(True, description="Include cooldowns"),
):
    try:
        return search_similar_workouts(query, top_k, include_warmups, include_cooldowns)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
