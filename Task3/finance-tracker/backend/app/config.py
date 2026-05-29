# backend/app/config.py
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

class Settings:
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    API_KEY: str = os.getenv("API_KEY", "")
    PROVIDER: str = os.getenv("PROVIDER", "gemini")
    # Add other configuration as needed

settings = Settings()
