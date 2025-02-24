.PHONY: setup run clean embeddings load_embeddings

# Install dependencies and prepare the environment
setup:
	poetry install
	poetry run python backend/core/create_embeddings.py --input_dir=data --output_dir=faiss_index --track_mapping=track_mapping.json
	poetry run python backend/core/load_embeddings.py

# Run the API server
run:
	poetry run uvicorn backend.main:app --reload

# Create FAISS embeddings from workout data
embeddings:
	poetry run python backend/core/create_embeddings.py --input_dir=data --output_dir=faiss_index --track_mapping=track_mapping.json

# Load FAISS embeddings into the app
load_embeddings:
	poetry run python backend/core/load_embeddings.py

# Clean up cached embeddings
clean:
	rm -rf faiss_index/*
