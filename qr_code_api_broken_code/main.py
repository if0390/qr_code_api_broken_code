from fastapi import FastAPI
from dotenv import load_dotenv
from app.config import QR_DIRECTORY
from app.routers import qr_code, oauth
from app.services.qr_service import create_directory
from app.utils.common import setup_logging

# Load environment variables
load_dotenv()

# Set up logging
setup_logging()

# Ensure QR code directory exists
create_directory(QR_DIRECTORY)

# Create FastAPI app
app = FastAPI(
    title="QR Code Manager",
    description="An API for creating, listing, and deleting QR codes with secure access.",
    version="1.0.0",
    redoc_url="/redoc",
    contact={
        "name": "API Support",
        "url": "http://yourdomain.com/support",
        "email": "support@yourdomain.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# Include routers
app.include_router(qr_code.router, prefix="/qr-codes", tags=["QR Code Management"])
app.include_router(oauth.router, prefix="", tags=["Authentication"])  # Includes /token at root

# Health check endpoint
@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "API is running"}
