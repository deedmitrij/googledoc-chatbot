import os
from pathlib import Path
from dotenv import load_dotenv

# Get the project's root directory
PROJECT_ROOT = Path(__file__).resolve().parent

# Load environment variables from .env file
load_dotenv(PROJECT_ROOT / ".env")

# Google Credentials Path
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")

# HuggingFace API Key
HF_API_KEY = os.getenv('HF_API_KEY')

# If a relative path is provided, resolve it based on the project root
if not os.path.isabs(GOOGLE_CREDENTIALS_PATH):
    GOOGLE_CREDENTIALS_PATH = PROJECT_ROOT / GOOGLE_CREDENTIALS_PATH

# Validate API Key
if not HF_API_KEY:
    raise ValueError('HF_API_KEY is not set. Please configure it in the .env file.')

# Validate Credentials File Path
if not os.path.exists(GOOGLE_CREDENTIALS_PATH):
    raise FileNotFoundError(
        f'Google API credentials not found at "{GOOGLE_CREDENTIALS_PATH}". Please check your .env file.'
    )
