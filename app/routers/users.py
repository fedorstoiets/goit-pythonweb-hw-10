from fastapi import APIRouter, Depends, File, UploadFile, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.dependencies import get_current_user, get_db
from app.models import User
from app.schemas import UserResponse
from app.services.cloudinary_service import upload_avatar

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
)

limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/me",
    response_model=UserResponse,
)
@limiter.limit("5/minute")
def read_me(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return current_user


@router.patch(
    "/avatar",
    response_model=UserResponse,
)
def update_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    avatar_url = upload_avatar(file, current_user.id)
    current_user.avatar_url = avatar_url
    db.commit()
    db.refresh(current_user)
    return current_user
