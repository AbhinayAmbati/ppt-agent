"""
Authentication service: JWT token generation, validation, user management
"""

from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from config import get_settings
from db import get_user_by_username, authenticate_user, create_user as db_create_user
from auth.schemas import UserResponse, TokenData

settings = get_settings()


def create_access_token(user_id: str) -> str:
    """Create JWT access token"""
    expires = datetime.utcnow() + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode = {
        "sub": str(user_id),
        "exp": expires,
        "type": "access"
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str) -> TokenData | None:
    """Verify and decode JWT access token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        token_data = TokenData(sub=user_id)
    except (JWTError, ValueError):
        return None
    return token_data


def register_user(db: Session, username: str, email: str, password: str) -> UserResponse | None:
    """Register new user"""
    # Check if user already exists
    if get_user_by_username(db, username):
        return None  # User already exists

    # Create user
    user = db_create_user(db, username, email, password)
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


def login_user(db: Session, username: str, password: str) -> tuple[str, UserResponse] | None:
    """Login user and return access token"""
    user = authenticate_user(db, username, password)
    if not user:
        return None

    # Create token
    token = create_access_token(user.id)

    user_response = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

    return token, user_response
