import logging.config
import os
import base64
from typing import List, Optional, Any
from dotenv import load_dotenv
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from app.config import ADMIN_PASSWORD, ADMIN_USER, ALGORITHM, SECRET_KEY
from urllib.parse import urlparse
from pydantic import AnyUrl

# Load environment variables from .env file
load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def setup_logging():
    logging_config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'logging.conf')
    normalized_path = os.path.normpath(logging_config_path)
    if not os.path.exists(normalized_path):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.warning(f"Default logging configured; missing logging configuration file at: {normalized_path}")
    else:
        logging.config.fileConfig(normalized_path, disable_existing_loggers=False)


def authenticate_user(username: str, password: str) -> Optional[dict]:
    if username == ADMIN_USER and password == ADMIN_PASSWORD:
        return {"username": username}
    logging.warning(f"Authentication failed for user: {username}")
    return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta and expires_delta <= timedelta(0):
        logging.error("Token expiration must be a positive timedelta.")
        raise ValueError("Token expiration must be a positive timedelta.")
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    logging.info(f"Token created with expiration: {expire}")
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def validate_and_sanitize_url(url_str: Any) -> Optional[str]:
    """
    Validates and sanitizes a given URL string or object.
    Ensures the URL has a valid scheme ('http' or 'https') and a non-empty netloc.
    """
    # Convert Url object to string if necessary
    if isinstance(url_str, (AnyUrl, urlparse('').__class__)):
        url_str = str(url_str)

    try:
        parsed_url = urlparse(url_str)
        if parsed_url.scheme in {"http", "https"} and parsed_url.netloc:
            logging.info(f"URL validated successfully: {url_str}")
            return url_str
        else:
            logging.error(f"Validation failed: URL must have a valid scheme and netloc - {url_str}")
            return None
    except Exception as e:
        logging.error(f"Exception during URL validation: {e}")
        return None


def encode_url_to_filename(url: Any) -> str:
    """
    Encodes a URL into a safe filename using base64 encoding.
    """
    sanitized_url = validate_and_sanitize_url(url)
    if sanitized_url is None:
        raise ValueError("Invalid URL. Cannot encode.")
    encoded_bytes = base64.urlsafe_b64encode(sanitized_url.encode('utf-8'))
    filename = encoded_bytes.decode('utf-8').rstrip('=')
    logging.info(f"URL encoded to filename: {filename}")
    return filename


def decode_filename_to_url(encoded_str: str) -> str:
    try:
        padding_needed = 4 - (len(encoded_str) % 4)
        if padding_needed:
            encoded_str += "=" * padding_needed
        decoded_bytes = base64.urlsafe_b64decode(encoded_str)
        url = decoded_bytes.decode('utf-8')
        logging.info(f"Filename decoded to URL: {url}")
        return url
    except (base64.binascii.Error, UnicodeDecodeError) as e:
        logging.error(f"Error decoding filename to URL: {e}")
        raise ValueError("Invalid encoded string provided.")


def generate_links(action: str, qr_filename: str, base_api_url: str, download_url: str) -> List[dict]:
    filename, ext = os.path.splitext(qr_filename)
    if ext != '.png':
        raise ValueError("QR filename must have a .png extension.")
    try:
        original_url = decode_filename_to_url(filename)
    except ValueError:
        logging.warning(f"Filename could not be decoded to a URL: {qr_filename}")
        original_url = None

    links = []
    if action in ["list", "create"]:
        links.append({"rel": "view", "href": download_url, "action": "GET", "type": "image/png"})
    if action in ["list", "create", "delete"]:
        delete_url = f"{base_api_url}/qr-codes/{qr_filename}"
        links.append({"rel": "delete", "href": delete_url, "action": "DELETE", "type": "application/json"})
    logging.info(f"Links generated: {links}")
    return links


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logging.error("Invalid token: Missing subject field.")
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        logging.info(f"Authenticated user: {username}")
        return {"username": username}
    except JWTError as e:
        logging.error(f"JWT decoding error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
