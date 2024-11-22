from pydantic import BaseModel, HttpUrl, Field, ConfigDict, conint, field_validator
from typing import List, Optional


class QRCodeRequest(BaseModel):
    """
    Schema for incoming QR code generation requests.
    """
    url: HttpUrl = Field(..., description="The URL to encode into the QR code.")
    fill_color: str = Field(default="red", description="Color of the QR code.")
    back_color: str = Field(default="white", description="Background color of the QR code.")
    size: conint(ge=1, le=40) = Field(default=10, description="Size of the QR code grid, must be between 1 and 40.")

    @field_validator("fill_color", "back_color")
    def validate_color(cls, value: str) -> str:
        """
        Validates that the provided colors are non-empty strings.
        Additional checks (e.g., valid hex color codes) could be implemented here.
        """
        if not value.strip():
            raise ValueError("Color cannot be an empty string.")
        return value

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "url": "https://example.com",
                "fill_color": "black",
                "back_color": "yellow",
                "size": 20,
            }
        }
    )


class Link(BaseModel):
    """
    Schema for HATEOAS (Hypermedia As The Engine Of Application State) links.
    """
    rel: str = Field(..., description="Relation type of the link (e.g., 'self', 'next').")
    href: HttpUrl = Field(..., description="The URL of the link.")
    action: str = Field(..., description="HTTP method for the action this link represents.")
    type: str = Field(default="application/json", description="Content type of the response for this link.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rel": "self",
                "href": "https://api.example.com/qr/123",
                "action": "GET",
                "type": "application/json",
            }
        }
    )


class QRCodeResponse(BaseModel):
    """
    Schema for QR code generation responses.
    """
    message: str = Field(..., description="A message related to the QR code request.")
    qr_code_url: HttpUrl = Field(..., description="The URL to the generated QR code image.")
    links: List[Link] = Field(default=[], description="HATEOAS links related to the QR code resource.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "QR code created successfully.",
                "qr_code_url": "https://api.example.com/qr/123",
                "links": [
                    {
                        "rel": "self",
                        "href": "https://api.example.com/qr/123",
                        "action": "GET",
                        "type": "application/json",
                    }
                ],
            }
        }
    )


class Token(BaseModel):
    """
    Schema for authentication tokens.
    """
    access_token: str = Field(..., description="The access token for authentication.")
    token_type: str = Field(default="bearer", description="Type of token.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "jhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }
    )


class TokenData(BaseModel):
    """
    Schema for data extracted from tokens.
    """
    username: Optional[str] = Field(None, description="The username that the token represents.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "user@example.com",
            }
        }
    )
