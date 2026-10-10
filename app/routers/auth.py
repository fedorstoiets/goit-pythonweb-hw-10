import jwt
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud
from app.dependencies import get_db
from app.models import User
from app.schemas import (
    LoginRequest,
    MessageResponse,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from app.security import (
    create_access_token,
    create_email_verification_token,
    decode_email_verification_token,
    verify_password,
)
from app.services.email import send_verification_email

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> UserResponse:
    if crud.get_user_by_email(db, str(user_data.email)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    try:
        user = crud.create_user(db, user_data)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        ) from exc

    verification_token = create_email_verification_token(user.id)
    background_tasks.add_task(
        send_verification_email,
        user.email,
        user.username,
        verification_token,
    )

    return user


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    user = crud.get_user_by_email(db, str(login_data.email))

    if user is None or not verify_password(
        login_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user.id)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


@router.get(
    "/verify-email",
    response_model=MessageResponse,
)
def verify_email(
    token: str,
    db: Session = Depends(get_db),
) -> MessageResponse:
    try:
        user_id = decode_email_verification_token(token)
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token.",
        )

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    if user.is_verified:
        return MessageResponse(message="Email is already verified.")

    user.is_verified = True
    db.commit()

    return MessageResponse(message="Email verified successfully.")


@router.post(
    "/resend-verification",
    response_model=MessageResponse,
)
def resend_verification(
    email: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> MessageResponse:
    user = crud.get_user_by_email(db, email)

    if user is not None and not user.is_verified:
        verification_token = create_email_verification_token(user.id)
        background_tasks.add_task(
            send_verification_email,
            user.email,
            user.username,
            verification_token,
        )

    return MessageResponse(
        message="If the account exists and is unverified, a verification email was sent."
    )
