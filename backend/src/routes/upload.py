"""File upload routes."""

import base64
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel

from ..services.files import file_service
from ..middleware.auth import get_current_user
from fastapi import Depends


router = APIRouter(prefix="/upload", tags=["upload"])


class ImageUploadResponse(BaseModel):
    """Response for image upload."""

    url: str
    type: str
    size: int


class Base64UploadRequest(BaseModel):
    """Request for base64 image upload."""

    data: str  # Base64 encoded image data


@router.post("/image", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
):
    """
    Upload an image file.
    Supports JPEG, PNG, WebP, and GIF up to 10MB.
    """
    # Validate content type
    if file.content_type not in file_service.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not allowed. Allowed: JPEG, PNG, WebP, GIF",
        )

    # Read file
    content = await file.read()

    # Validate size
    if len(content) > file_service.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {file_service.MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    # Encode to base64
    base64_data = base64.b64encode(content).decode("utf-8")
    data_url = f"data:{file.content_type};base64,{base64_data}"

    return ImageUploadResponse(
        url=data_url,
        type=file.content_type,
        size=len(content),
    )


@router.post("/image/base64", response_model=ImageUploadResponse)
async def upload_image_base64(
    request: Base64UploadRequest,
    user_id: str = Depends(get_current_user),
):
    """
    Upload an image using base64 encoding.
    The data should include the data URL prefix (e.g., 'data:image/png;base64,...')
    or just the raw base64 string.
    """
    try:
        data_url = file_service.save_base64_image(request.data)
        info = file_service.get_image_info(data_url)

        return ImageUploadResponse(
            url=data_url,
            type=info["type"],
            size=info["size"],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
