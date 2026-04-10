"""File service for handling uploads."""

import base64
import uuid
import os
from pathlib import Path


class FileService:
    """Service for file operations."""

    # Allowed image types
    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}

    # Max file size (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def validate_image(self, content_type: str, file_size: int) -> tuple[bool, str]:
        """Validate image type and size."""
        if content_type not in self.ALLOWED_IMAGE_TYPES:
            return (
                False,
                f"File type {content_type} not allowed. Allowed: JPEG, PNG, WebP, GIF",
            )

        if file_size > self.MAX_FILE_SIZE:
            return (
                False,
                f"File too large. Max size: {self.MAX_FILE_SIZE // (1024 * 1024)}MB",
            )

        return True, ""

    def save_base64_image(
        self, base64_data: str, content_type: str = "image/png"
    ) -> str:
        """
        Save a base64 encoded image and return the data URL.
        The base64_data should be in format: 'data:image/png;base64,<data>'
        or just the raw base64 string.
        """
        # Extract base64 data if it includes header
        if "," in base64_data:
            header, data = base64_data.split(",", 1)
            # Try to extract content type from header
            if "image/" in header:
                content_type = header.split(";")[0].replace("data:", "")
        else:
            data = base64_data

        # Validate
        is_valid, error = self.validate_image(content_type, len(data) * 3 // 4)
        if not is_valid:
            raise ValueError(error)

        # Generate filename
        ext = content_type.split("/")[-1]
        if ext == "jpeg":
            ext = "jpg"
        filename = f"{uuid.uuid4()}.{ext}"

        # Save file
        filepath = self.upload_dir / filename
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(data))

        # Return data URL
        return f"data:{content_type};base64,{data}"

    def get_image_info(self, data_url: str) -> dict:
        """Get basic info about an image from its data URL."""
        if not data_url.startswith("data:"):
            return {"type": "unknown", "size": 0}

        header = data_url.split(",")[0]
        content_type = header.replace("data:", "").split(";")[0]
        base64_data = data_url.split(",")[1] if "," in data_url else ""

        # Estimate size (base64 is ~4/3 of binary)
        size = len(base64_data) * 3 // 4

        return {
            "type": content_type,
            "size": size,
            "is_image": content_type in self.ALLOWED_IMAGE_TYPES,
        }


file_service = FileService()
