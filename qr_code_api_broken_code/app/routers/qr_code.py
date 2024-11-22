from fastapi import APIRouter, HTTPException, Depends, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from typing import List
from app.schema import QRCodeRequest, QRCodeResponse
from app.services.qr_service import generate_qr_code, list_qr_codes, delete_qr_code
from app.utils.common import encode_url_to_filename, get_current_user
from app.config import QR_DIRECTORY, SERVER_BASE_URL, FILL_COLOR, BACK_COLOR, SERVER_DOWNLOAD_FOLDER
import logging

# OAuth2 setup with token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# APIRouter instance
router = APIRouter()

@router.post("/", response_model=QRCodeResponse, status_code=status.HTTP_201_CREATED)
async def create_qr_code(request: QRCodeRequest, token: str = Depends(oauth2_scheme)):
    """
    Create a new QR code for a given URL.
    """
    logging.info(f"Creating QR code for: {request.url}")
    current_user = get_current_user(token)

    encoded_url = encode_url_to_filename(request.url)
    qr_filename = f"{encoded_url}.png"
    qr_code_full_path = QR_DIRECTORY / qr_filename

    if qr_code_full_path.exists():
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": "QR code already exists."}
        )

    try:
        generate_qr_code(
            data=request.url,
            path=qr_code_full_path,
            fill_color=FILL_COLOR,
            back_color=BACK_COLOR,
            size=request.size
        )
    except Exception as e:
        logging.exception("Error generating QR code")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating QR code: {str(e)}"
        )

    qr_code_url = f"{SERVER_BASE_URL}/{SERVER_DOWNLOAD_FOLDER}/{qr_filename}"
    return QRCodeResponse(
        message="QR code created successfully.",
        qr_code_url=qr_code_url
    )

@router.get("/", response_model=List[QRCodeResponse])
async def list_qr_codes_endpoint(token: str = Depends(oauth2_scheme)):
    """
    List all available QR codes.
    """
    current_user = get_current_user(token)

    try:
        qr_files = list_qr_codes(QR_DIRECTORY)
    except Exception as e:
        logging.exception("Error listing QR codes")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing QR codes: {str(e)}"
        )

    return [
        QRCodeResponse(
            message="QR code available.",
            qr_code_url=f"{SERVER_BASE_URL}/{SERVER_DOWNLOAD_FOLDER}/{qr_file}"
        )
        for qr_file in qr_files
    ]

@router.delete("/{qr_filename}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_qr_code_endpoint(qr_filename: str, token: str = Depends(oauth2_scheme)):
    """
    Delete a specific QR code.
    """
    current_user = get_current_user(token)

    qr_code_path = QR_DIRECTORY / qr_filename
    if not qr_code_path.exists():
        logging.error(f"QR code {qr_filename} not found for deletion")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR code not found."
        )

    try:
        delete_qr_code(qr_code_path)
    except Exception as e:
        logging.exception("Error deleting QR code")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting QR code: {str(e)}"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
