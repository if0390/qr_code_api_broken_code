# Load environment variables
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Environment Variables for Configuration
QR_DIRECTORY = Path(os.getenv("QR_DIRECTORY", './qr_codes')).resolve()

FILL_COLOR = os.getenv("FILL_COLOR", 'red')
BACK_COLOR = os.getenv("BACK_COLOR", 'white')

SERVER_BASE_URL = os.getenv("SERVER_BASE_URL", 'http://localhost:80')
SERVER_DOWNLOAD_FOLDER = os.getenv("SERVER_DOWNLOAD_FOLDER", 'downloads')

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set!")

ALGORITHM = os.getenv("ALGORITHM", "HS256")

try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
except ValueError:
    raise ValueError("Invalid ACCESS_TOKEN_EXPIRE_MINUTES value in .env file.")

ADMIN_USER = os.getenv('ADMIN_USER')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
if not ADMIN_USER or not ADMIN_PASSWORD:
    raise ValueError("ADMIN_USER and ADMIN_PASSWORD must be set in the environment.")
