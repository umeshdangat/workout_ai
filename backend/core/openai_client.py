import openai
import os
import time
from dotenv import load_dotenv

# Load API key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API Key. Set OPENAI_API_KEY in .env")

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Rate limiting
MIN_TIME_BETWEEN_REQUESTS = 20  # seconds
_last_request_time = 0

def call_openai_api(prompt: str) -> str:
    """
    Calls OpenAI API with a given prompt and returns raw JSON response.
    """
    global _last_request_time

    time_since_last_request = time.time() - _last_request_time
    if time_since_last_request < MIN_TIME_BETWEEN_REQUESTS:

        time.sleep(MIN_TIME_BETWEEN_REQUESTS - time_since_last_request)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a fitness coach generating structured training programs."},
                  {"role": "user", "content": prompt}],
        temperature=0.7,
    )

    _last_request_time = time.time()
    return response.choices[0].message.content.strip()
