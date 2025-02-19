import json
import os

import faiss
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

# Paths for FAISS Index & Metadata
INDEX_DIR = os.getenv("FAISS_INDEX_DIR", "data_ingestion/faiss_index")
FAISS_INDEX_PATH = f"{INDEX_DIR}/workout_embeddings.index"
METADATA_PATH = f"{INDEX_DIR}/workout_metadata.json"

# Load Model
MODEL_NAME = "BAAI/bge-large-en-v1.5"
model = SentenceTransformer(MODEL_NAME)

# Load FAISS index
def load_faiss_index():
    try:
        return faiss.read_index(FAISS_INDEX_PATH)
    except Exception as e:
        raise RuntimeError(f"Failed to load FAISS index: {str(e)}")

index = load_faiss_index()

# Load metadata
def load_metadata():
    try:
        with open(METADATA_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load metadata JSON: {str(e)}")

workout_metadata = load_metadata()
