from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, ADMIN_USER, ADMIN_PASSWORD
from app.schema import Token
from app.utils.common import create_access_token, authenticate_user

# OAuth2 configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")  # Ensure tokenUrl points to "/token"
router = APIRouter()

@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint to authenticate user and generate an access token.
    :param form_data: OAuth2 password form containing username and password
    :return: Access token and token type
    """
    # Authenticate the user
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},  # Required header for OAuth2
        )
    
    # Set token expiration time
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Create the access token
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires
    )

    # Return the token in the defined schema
    return Token(access_token=access_token, token_type="bearer")
