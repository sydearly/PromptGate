import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_DISCOVERY_URL = os.getenv("GOOGLE_DISCOVERY_URL")

    # Allow local insecure transport for development
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = os.getenv("OAUTHLIB_INSECURE_TRANSPORT", "0")

    # Rate Limiting & Logs
    RATE_LIMIT = os.getenv("RATE_LIMIT", "10 per minute")
    LOG_PATH = os.getenv("LOG_PATH", "server/data/events.jsonl")

    # Sessions
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
