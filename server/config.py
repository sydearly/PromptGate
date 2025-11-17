# server/config.py
import os
from datetime import timedelta

# Optional: only load .env locally
if os.getenv("USE_DOTENV", "0") == "1":
    try:
        from dotenv import load_dotenv  # add python-dotenv to requirements if you use this
        load_dotenv()
    except Exception:
        pass

class Config:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"

    # OpenAI (allow empty default so import never crashes)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # Google OAuth (safe defaults)
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_DISCOVERY_URL = os.getenv("GOOGLE_DISCOVERY_URL", "")

    # Rate limiting & logs
    RATE_LIMIT = os.getenv("RATE_LIMIT", "10 per minute")
    LOG_PATH = os.getenv("LOG_PATH", "server/data/events.jsonl")

    # Sessions
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

    # CORS / origin
    ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "http://127.0.0.1:5000")
