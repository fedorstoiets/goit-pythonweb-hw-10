import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile, status

from app.config import get_settings

settings = get_settings()


def upload_avatar(file: UploadFile, user_id: int) -> str:
    if not all(
        [
            settings.cloudinary_cloud_name,
            settings.cloudinary_api_key,
            settings.cloudinary_api_secret,
        ]
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Cloudinary is not configured. Add Cloudinary credentials "
                "to the .env file."
            ),
        )

    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )

    result = cloudinary.uploader.upload(
        file.file,
        public_id=f"hw10/users/{user_id}/avatar",
        overwrite=True,
        resource_type="image",
        transformation=[
            {
                "width": 250,
                "height": 250,
                "crop": "fill",
                "gravity": "face",
            }
        ],
    )

    return result["secure_url"]
