import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the YouTube to Buzzsprout application."""
    
    # Buzzsprout API settings
    BUZZSPROUT_API_TOKEN = os.getenv('BUZZSPROUT_API_TOKEN')
    BUZZSPROUT_PODCAST_ID = os.getenv('BUZZSPROUT_PODCAST_ID')
    BUZZSPROUT_API_BASE = 'https://www.buzzsprout.com/api'
    
    # Application settings
    UPLOAD_DIR = os.getenv('UPLOAD_DIR', './uploads')
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB limit
    ALLOWED_AUDIO_FORMATS = ['mp3', 'wav', 'm4a', 'aac']
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    @classmethod
    def validate_buzzsprout_config(cls):
        """Validate that required Buzzsprout credentials are present."""
        if not cls.BUZZSPROUT_API_TOKEN:
            raise ValueError("BUZZSPROUT_API_TOKEN environment variable is required")
        if not cls.BUZZSPROUT_PODCAST_ID:
            raise ValueError("BUZZSPROUT_PODCAST_ID environment variable is required")
        return True
    
    @classmethod
    def ensure_upload_dir(cls):
        """Ensure the upload directory exists."""
        os.makedirs(cls.UPLOAD_DIR, exist_ok=True)
        return cls.UPLOAD_DIR