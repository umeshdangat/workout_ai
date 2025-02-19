import argparse
import json
import os
import time
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("SUGARWOD_API_KEY")
BASE_URL = "https://api.sugarwod.com/v2"

HEADERS = {"Authorization": API_KEY}

# Define Default Date Range
DEFAULT_START_DATE = "20170101"
DEFAULT_END_DATE = "20171231"


def fetch_workouts(start_date, end_date):
    """Fetch workouts from SugarWOD API for a given date range."""
    url = f"{BASE_URL}/workouts?dates={start_date}-{end_date}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print(f"❌ Error fetching workouts {start_date}-{end_date}: {response.status_code}")
        return []


def fetch_tracks():
    """Fetch track names from SugarWOD API."""
    url = f"{BASE_URL}/tracks"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        tracks = response.json().get("data", [])
        track_mapping = {track["id"]: track["attributes"]["name"] for track in tracks}
        return track_mapping
    else:
        print(f"❌ Error fetching tracks: {response.status_code}")
        return {}


def main(output_dir, start_date, end_date):
    """Fetch and save workouts in batches."""
    os.makedirs(output_dir, exist_ok=True)

    # Fetch and save tracks
    tracks_file = os.path.join(output_dir, "tracks.json")
    if not os.path.exists(tracks_file):
        print("📡 Fetching available tracks from SugarWOD...")
        track_mapping = fetch_tracks()
        with open(tracks_file, "w") as f:
            json.dump(track_mapping, f, indent=4)
        print(f"✅ Saved track mappings to {tracks_file}")
    else:
        print(f"📂 Using cached track mappings from {tracks_file}")

    # Process workouts
    start_dt = datetime.strptime(start_date, "%Y%m%d")
    end_dt = datetime.strptime(end_date, "%Y%m%d")

    current_date = start_dt
    while current_date <= end_dt:
        next_week = current_date + timedelta(days=6)
        date_range = f"{current_date.strftime('%Y%m%d')}-{next_week.strftime('%Y%m%d')}"

        print(f"📡 Fetching workouts for {date_range}...")
        workouts = fetch_workouts(current_date.strftime('%Y%m%d'), next_week.strftime('%Y%m%d'))

        file_path = os.path.join(output_dir, f"workouts_{current_date.strftime('%Y%m%d')}.json")
        with open(file_path, "w") as f:
            json.dump(workouts, f, indent=4)

        print(f"✅ Saved {len(workouts)} workouts to {file_path}")

        current_date = next_week + timedelta(days=1)
        time.sleep(1)  # Respect API rate limits


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch SugarWOD workouts and save to JSON files.")
    parser.add_argument("--output-dir", type=str, required=True, help="Directory to store workout JSON files")
    parser.add_argument("--start-date", type=str, default=DEFAULT_START_DATE, help="Start date (YYYYMMDD)")
    parser.add_argument("--end-date", type=str, default=DEFAULT_END_DATE, help="End date (YYYYMMDD)")

    args = parser.parse_args()
    main(args.output_dir, args.start_date, args.end_date)
