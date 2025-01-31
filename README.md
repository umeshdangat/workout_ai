**🚀 AI-Powered Adaptive Strength & HIIT Training | WorkoutAI**  

WorkoutAI is an **open-source adaptive strength and conditioning platform** that **dynamically adjusts workouts in real-time** based on user feedback. Built with **FastAPI, PostgreSQL (Docker), and OpenAI GPT-4**, it personalizes **progressive overload weightlifting & HIIT programs**, making training smarter and more effective.

### **🔹 Features**
✅ **Custom 6-10 Week Periodized Workout Plans** – Strength & HIIT routines optimized for performance  
✅ **Real-Time Mid-Workout Adjustments** – Modify sets, reps, and intensity dynamically  
✅ **AI-Powered Adaptation** – Uses GPT-4 to generate & fine-tune workouts  
✅ **User Progress Tracking** – Store & analyze training data in a PostgreSQL database  
✅ **REST API-First Design** – Easily integrates with chatbots, mobile apps, or wearables  
✅ **Structured, Type-Safe Python Code** – Built following **Fluent Python** best practices  

### **🛠 Tech Stack**
- **FastAPI** (Lightweight async backend)  
- **PostgreSQL (Docker)** (Workout & user data storage)  
- **OpenAI GPT-4 API** (Dynamic program generation & feedback adjustments)  
- **Poetry** (Modern Python dependency management)  
- **Pydantic** (Strict type validation)  
- **Alembic** (Database migrations)  

### **🚀 Get Started**
1️⃣ Clone the repo:  
   ```bash
   git clone https://github.com/umeshdangat/workout-ai.git
   cd workout-ai
   ```  
2️⃣ Install dependencies (using Poetry):  
   ```bash
   poetry install
   ```  
3️⃣ Start PostgreSQL with Docker:  
   ```bash
   docker-compose up -d
   ```  
4️⃣ Run the API server:  
   ```bash
   poetry run uvicorn backend.main:app --reload
   ```  
5️⃣ Generate a workout via API:  
   - `POST /generate` → Creates a **personalized training program**  
   - `POST /update` → **Modifies** the plan in real-time based on feedback  

### **👥 Who’s It For?**
🏋️‍♂️ **Strength Athletes** – Powerlifters, CrossFitters, Olympic lifters  
🔥 **HIIT Enthusiasts** – Fitness-focused users who want structured cardio + lifting  
💡 **AI & Fitness Developers** – Those interested in applying LLMs to training  

---

Would you like to **add user authentication (OAuth2/JWT) next** or focus on **a chatbot interface**? 🚀
