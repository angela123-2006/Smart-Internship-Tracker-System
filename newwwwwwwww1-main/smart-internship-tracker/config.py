"""
==============================================================
Smart Internship Tracker System — Configuration
==============================================================
Loads environment variables and provides app-wide settings.
==============================================================
"""

import os
from dotenv import load_dotenv

# Load variables from .env file into the environment
load_dotenv()


class Config:
    """Central configuration loaded from environment variables."""

    # --- Flask ---
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    PORT = int(os.getenv("FLASK_PORT", 5000))

    # --- MySQL Database ---
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "internship_tracker")
