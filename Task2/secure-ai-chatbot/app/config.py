# app/config.py
# Central configuration loader for environment variables and model settings.

import os
from dotenv import load_dotenv

# Load variables from .env file if present
load_dotenv()


class Config:
    """
    Holds all configuration constants for the chatbot application.
    Values are read from environment variables with safe defaults.
    """

    # --- API Configuration ---
    # Supports Google Gemini (free) or OpenAI (paid).
    # Set PROVIDER to "gemini" or "openai" in your .env file.
    PROVIDER: str = os.getenv("PROVIDER", "gemini")

    # Google Gemini free API key (get from https://aistudio.google.com/apikey)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # OpenAI API key (optional alternative)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    # --- App Settings ---
    APP_TITLE: str = "Secure AI Chatbot"
    APP_VERSION: str = "1.0.0"
    MAX_INPUT_LENGTH: int = 1000  # Max characters allowed per user message

    # --- Safety Settings ---
    # Risk levels returned in JSON output
    RISK_LEVEL_LOW: str = "low"
    RISK_LEVEL_MEDIUM: str = "medium"
    RISK_LEVEL_HIGH: str = "high"

    # Path to prompt files
    PROMPTS_DIR: str = os.path.join(os.path.dirname(__file__), "..", "prompts")

    @staticmethod
    def load_prompt(filename: str) -> str:
        """
        Reads and returns the content of a prompt text file.

        Args:
            filename: Name of the .txt file inside the prompts/ directory.

        Returns:
            The prompt string, or an empty string if the file is missing.
        """
        path = os.path.join(Config.PROMPTS_DIR, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            print(f"[WARNING] Prompt file not found: {path}")
            return ""


# Single shared config instance
config = Config()
