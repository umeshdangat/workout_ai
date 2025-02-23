from backend.core.load_embeddings import model, index, workout_metadata
from backend.services.workout_category import get_workout_category


def search_similar_workouts(query: str, top_k: int, include_warmups: bool = True, include_cooldowns: bool = False):
    query_embedding = model.encode([query], convert_to_numpy=True)

    distances, indices = index.search(query_embedding, top_k)

    results, warmups, cooldowns = [], [], []

    for i, idx in enumerate(indices[0]):
        if idx < len(workout_metadata):
            workout = workout_metadata[idx]
            workout_category = get_workout_category(workout)

            result = {
                "rank": i + 1,
                "title": workout["title"],
                "description": workout["description"],
                "score_type": workout["score_type"],
                "workout_type": workout["workout_type"],
                "track": workout["track"],
                "created_at": workout["created_at"],
                "distance": float(distances[0][i]),
            }

            if workout_category == "warmup" and include_warmups:
                warmups.append(result)
            elif workout_category == "quality" and include_cooldowns:
                cooldowns.append(result)
            else:
                results.append(result)

    return {
        "query": query,
        "results": results,
        "warmups": warmups,
        "for quality": cooldowns
    }


def search_similar_workouts_text(query: str, top_k: int = 100) -> str:
    """
    Search for similar workouts using FAISS and return a textual summary for RAG.
    """
    query_embedding = model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_embedding, top_k)

    retrieved_workouts = []

    for i, idx in enumerate(indices[0]):
        if idx < len(workout_metadata):
            workout = workout_metadata[idx]
            retrieved_workouts.append(
                f"{workout['title']} - {workout['description']} | Type: {workout['workout_type']} | Score: {workout['score_type']} | Track: {workout['track']} | Date: {workout['created_at']}"
            )

    return "\n".join(retrieved_workouts) if retrieved_workouts else "No similar workouts found."
