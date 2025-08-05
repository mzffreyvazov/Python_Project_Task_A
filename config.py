import os
from datetime import timedelta


class Config:
    # Flask app configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'nazirlik_ai_secret_key_2025'

    # Gemini API configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or "AIzaSyAk5UaULKxoV3CahPftPIwQA2Io4Ph3nno"

    # Database configuration
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or 'users.db'

    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # Debug mode - False for production
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    # Server configuration
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', os.environ.get('FLASK_PORT', 5000)))

    # Templates directory
    TEMPLATES_DIR = 'templates'