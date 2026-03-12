from typing import Annotated

from fastapi import APIRouter, Depends
from redis import Redis
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.redis import get_redis
from app.models.user import User
from app.schemas.auth import (
    AccessTokenAPIResponse,
    AccessTokenResponse,
    CurrentUserAPIResponse,
    CurrentUserResponse,
    LoginRequest,
    RefreshTokenRequest,
    TokenPairAPIResponse,
    TokenPairResponse,
)
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenPairAPIResponse)
async def login(
    payload: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> TokenPairAPIResponse:
    service = AuthService(db, redis)
    return TokenPairAPIResponse(data=service.login(email=payload.email, password=payload.password))


@router.get("/me", response_model=CurrentUserAPIResponse)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> CurrentUserAPIResponse:
    return CurrentUserAPIResponse(data=CurrentUserResponse.model_validate(current_user))


@router.post("/refresh", response_model=AccessTokenAPIResponse)
async def refresh_access_token(
    payload: RefreshTokenRequest,
    db: Annotated[Session, Depends(get_db)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> AccessTokenAPIResponse:
    service = AuthService(db, redis)
    return AccessTokenAPIResponse(data=service.refresh_access_token(payload.refresh_token))
