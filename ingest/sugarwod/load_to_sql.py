import os
import json
import mysql.connector
import argparse
from dotenv import load_dotenv

# Load database credentials from .env
load_dotenv()
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DB"),
}

def load_json_to_mysql(input_dir):
    """Load workout data from JSON files into MySQL."""
    db = mysql.connector.connect(**DB_CONFIG)
    cursor = db.cursor()

    json_files = [f for f in os.listdir(input_dir) if f.endswith(".json")]

    for file_name in json_files:
        file_path = os.path.join(input_dir, file_name)
        print(f"📂 Processing {file_name}...")

        with open(file_path, "r") as f:
            workouts = json.load(f)

        for workout in workouts:
            cursor.execute(
                "INSERT INTO workouts (id, title, description, track_id, score_type, scheduled_date, scheduled_at, movement_ids) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    workout["id"],
                    workout["title"],
                    workout["description"],
                    workout["track"]["id"],
                    workout["score_type"],
                    workout["scheduled_date_int"],
                    workout["scheduled_at"],
                    json.dumps(workout["movement_ids"]),
                )
            )

        db.commit()
        print(f"✅ Inserted {len(workouts)} workouts from {file_name} into MySQL.")

    cursor.close()
    db.close()
    print("✅ All workouts have been loaded into MySQL.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load SugarWOD JSON data into MySQL.")
    parser.add_argument("--input-dir", type=str, required=True, help="Directory containing workout JSON files")

    args = parser.parse_args()
    load_json_to_mysql(args.input_dir)
