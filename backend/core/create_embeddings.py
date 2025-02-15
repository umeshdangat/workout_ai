import argparse
import json
import os
from dataclasses import dataclass
from typing import Iterator, List, Dict

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load a larger embedding model with 1024 dimensions
MODEL_NAME = "BAAI/bge-large-en-v1.5"
model = SentenceTransformer(MODEL_NAME)


@dataclass
class Workout:
    """Represents a structured workout data entity for embedding."""
    id: str
    title: str
    description: str
    score_type: str
    workout_type: str
    track: str
    created_at: str

    def to_text(self) -> str:
        """Returns a textual representation suitable for embeddings."""
        return f"{self.title} - {self.description} | Type: {self.workout_type} | Score: {self.score_type} | Track: {self.track} | Date: {self.created_at}"


def parse_arguments() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Generate embeddings from SugarWOD extracted workouts")
    parser.add_argument("--input_dir", required=True, help="Path to extracted JSON files")
    parser.add_argument("--output_dir", required=True, help="Path to store FAISS index")
    parser.add_argument("--track_mapping", required=True, help="Path to JSON file containing track mappings")
    return parser.parse_args()


def load_track_mapping(track_mapping_path: str) -> Dict[str, str]:
    """Load track mappings from JSON file."""
    with open(track_mapping_path, "r") as f:
        return json.load(f)


def get_workout_type(score_type: str, title: str) -> str:
    """Decide workout type e.g. warmup, quality time, open gym """
    known_workout_types = ["pre-wod", "warmup", "quality time", "open gym"]
    for workout_type in known_workout_types:
        if workout_type in title.lower().strip():
            return workout_type
    return score_type if score_type else "N/A"


def load_workouts(input_dir: str, track_mapping: Dict[str, str]) -> Iterator[Workout]:
    """Lazy load workouts from JSON files."""
    for file in os.listdir(input_dir):
        if not (file.endswith(".json") and file.startswith("workouts")):
            continue

        with open(os.path.join(input_dir, file), "r") as f:
            try:
                data = json.load(f)
                if not isinstance(data, list):
                    continue
            except json.JSONDecodeError:
                print(f"⚠️ Skipping corrupt JSON file: {file}")
                continue

        for workout in data:
            attributes = workout.get("attributes", {})
            title = attributes.get("title", "Unknown Workout")
            description = attributes.get("description", "")
            score_type = attributes.get("score_type", "").strip().lower()
            track_id = attributes.get("track", {}).get("id", "unknown")
            track_name = track_mapping.get(track_id, "Unknown Track")
            created_at = attributes.get("created_at", "")

            # Classify workout type dynamically
            workout_type = get_workout_type(score_type, title)

            yield Workout(
                id=workout["id"],
                title=title,
                description=description,
                score_type=score_type,
                workout_type=workout_type,
                track=track_name,
                created_at=created_at,
            )


def create_embeddings(workouts: List[Workout]) -> np.ndarray:
    """Generate embeddings from textual workout descriptions."""
    texts = [workout.to_text() for workout in workouts]
    embeddings = model.encode(texts, convert_to_numpy=True)

    if not isinstance(embeddings, np.ndarray) or embeddings.ndim != 2:
        raise ValueError(
            f"🚨 Embeddings must be a 2D NumPy array. Got {type(embeddings)} with shape {embeddings.shape if isinstance(embeddings, np.ndarray) else None}")

    return embeddings


def store_faiss_index(embeddings: np.ndarray, output_path: str) -> None:
    """Store embeddings in FAISS index."""
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    faiss.write_index(index, output_path)


def main():
    """Main function for generating and storing embeddings."""
    args = parse_arguments()
    os.makedirs(args.output_dir, exist_ok=True)

    track_mapping = load_track_mapping(args.track_mapping)
    workouts = list(load_workouts(args.input_dir, track_mapping))

    print(f"✅ Loaded {len(workouts)} workouts. Generating embeddings...")

    embeddings = create_embeddings(workouts)

    # Save metadata
    metadata_path = os.path.join(args.output_dir, "workout_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump([workout.__dict__ for workout in workouts], f, indent=4)

    # Save FAISS index
    faiss_index_path = os.path.join(args.output_dir, "workout_embeddings.index")
    store_faiss_index(embeddings, faiss_index_path)

    print(f"✅ Indexed {len(workouts)} workouts and saved FAISS index to {faiss_index_path}")


if __name__ == "__main__":
    main()
