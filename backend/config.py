import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API Key & Credentials Path
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")

# Get the project's root directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# If a relative path is provided, resolve it based on the project root
if not os.path.isabs(GOOGLE_CREDENTIALS_PATH):
    GOOGLE_CREDENTIALS_PATH = PROJECT_ROOT / GOOGLE_CREDENTIALS_PATH

# Validate API Key
if not GEMINI_API_KEY:
    raise ValueError('GEMINI_API_KEY is not set. Please configure it in the .env file.')

# Validate Credentials File Path
if not os.path.exists(GOOGLE_CREDENTIALS_PATH):
    raise FileNotFoundError(
        f'Google API credentials not found at "{GOOGLE_CREDENTIALS_PATH}". Please check your .env file.'
    )
