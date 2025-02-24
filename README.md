# 🚀 WorkoutAI: AI-Powered Adaptive Strength & HIIT Training

WorkoutAI is an **open-source adaptive strength and conditioning platform** that dynamically adjusts workouts based on user feedback. Built with **FastAPI, FAISS, and OpenAI GPT-4**, it personalizes **progressive overload weightlifting & HIIT programs** using Retrieval-Augmented Generation (RAG).

## 👥 Who’s It For?
- 🏋️‍♂️ Strength Athletes – Powerlifters, CrossFitters, Olympic lifters
- 🔥 HIIT Enthusiasts – Fitness-focused users who want structured cardio + lifting
- 💡 AI & Fitness Developers – Those interested in applying LLMs to training

## **🔹 Features**
✅ **Custom 6-10 Week Periodized Workout Plans** – Strength & HIIT routines optimized for performance  
✅ **AI-Powered Adaptation** – Uses GPT-4 with FAISS-enhanced similarity retrieval
✅ **FAISS Vector Search** – Finds similar workouts from a **pre-indexed dataset**  
✅ **REST API-First Design** – Easily integrates with chatbots, mobile apps, or wearables  
✅ **Structured, Type-Safe Python Code** – Built following **Fluent Python** best practices
---

## **🛠 Tech Stack**
- **FastAPI** (Lightweight async backend)  
- **FAISS** (Efficient similarity search for workouts)
- **OpenAI GPT-4 API** (Dynamic workout generation)
- **Poetry** (Modern Python dependency management)  
- **Pydantic** (Strict type validation)  

---

## **🚀 Getting Started**
### **1️⃣ Clone the Repo**
```bash
git clone https://github.com/umeshdangat/workout-ai.git
cd workout-ai
```
### **2️⃣  Install Dependencies**
```bash
poetry install
```
### **3️⃣ Set Up Environment Variables**
Create a .env file in the project root and add:
```bash
FAISS_INDEX_DIR=faiss_index
OPENAI_API_KEY=your-api-key-here
```
### **4️⃣ Generate Workout Embeddings (Required for RAG)**
Before using the API, you must generate embeddings from SugarWOD workout data.
Run the following command to create embeddings and store them in FAISS:
```bash
poetry run python backend/core/create_embeddings.py --input_dir=data --output_dir=faiss_index --track_mapping=track_mapping.json
```
This process:
* Reads workouts from data/
* Converts them into vector embeddings using sentence-transformers
* Stores the indexed embeddings in faiss_index/

### **5️⃣ Load Embeddings into the App**
Once embeddings are created, load them into memory:
```bash
poetry run python backend/core/load_embeddings.py
```
### 6️⃣ Start the API Server
```bash
poetry run uvicorn backend.main:app --reload
```


## 📡 API Endpoints

### 1️⃣ Search Similar Workouts
```bash
GET /workouts/search_similar_workouts
```
Finds workouts similar to a given query using FAISS. Example Request:
```bash
curl -X GET "http://127.0.0.1:8000/workouts/search_similar_workouts?query=thrusters%20and%20burpees&top_k=5"
```
Example Response:
```bash
{
  "query": "thrusters and burpees",
  "results": [
    {
      "rank": 1,
      "title": "Fran",
      "description": "21-15-9 Thrusters & Pull-Ups",
      "score_type": "time",
      "workout_type": "WOD",
      "track": "CrossFit Main",
      "created_at": "2024-01-10",
      "distance": 0.312
    }
  ]
}
```

### 2️⃣ Generate AI-Powered Workout Plan
```bash
POST /workouts/generate
```
Generates a personalized training program using OpenAI + FAISS. Example Request:
```bash
curl -X POST "http://127.0.0.1:8000/workouts/generate" -H "Content-Type: application/json" -d '{
  "name": "Alex",
  "age": 30,
  "experience": "intermediate",
  "goals": ["increase endurance", "improve gymnastics"],
  "equipment": ["barbell", "pull-up bar", "rings"],
  "sessions_per_week": 5,
  "duration": 8
}'
```
Example Response:
```bash
{
  "name": "Alex's Plan",
  "weeks": [
    {
      "days": [
        {
          "sessions": [
            {
              "type": "WOD",
              "details": {
                "description": "5 Rounds of 10 Handstand Push-Ups, 15 KB Swings, 20 Double Unders",
                "intended_stimulus": "High-intensity with upper body endurance",
                "scaling_options": "Modify HSPU to pike push-ups, scale KB weight",
                "movements": [
                  {"description": "Handstand Push-Ups", "resources": "https://link.to/hspu"},
                  {"description": "Kettlebell Swings (24/16 kg)", "resources": "https://link.to/kbswings"},
                  {"description": "Double-Unders", "resources": "https://link.to/doubleunders"}
                ]
              }
            }
          ]
        }
      ]
    }
  ]
}
```

## 📂 Developer Workflow
### Run All Setup Steps at Once
You can automate everything using the Makefile:
```bash
make setup
```
This will:
- Install dependencies
- Generate embeddings
- Load FAISS index
- Start the API server
- To clean up all cached embeddings:
```bash
make clean
```

### 🛠 Troubleshooting
#### FAISS Index Not Found?
Ensure you ran:
```bash
poetry run python backend/core/create_embeddings.py
```

#### OpenAI API Key Missing?
Ensure your .env contains:
```bash
OPENAI_API_KEY=your-api-key-here
```

#### Poetry Issues?
Try reinstalling:
```bash
poetry env remove python
poetry install
```

#### Docker Issues?
Restart the container:
```bash
docker-compose restart
```