from backend.core.embeddings import model, index, workout_metadata


def get_workout_category(workout):
    title = workout["title"].lower().strip()
    score_type = workout["score_type"].strip().lower()

    if any(kw in title for kw in ["pre-wod", "warmup", "mobility"]):
        return "warmup"
    elif any(kw in title for kw in ["cooldown", "recovery", "stretch"]):
        return "cooldown"
    elif score_type:
        return "workout"
    return "other"


def search_similar_workouts(query: str, top_k: int, include_warmups: bool, include_cooldowns: bool):
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
