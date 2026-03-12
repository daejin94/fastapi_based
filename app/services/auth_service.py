from datetime import datetime

import jwt
from redis import Redis
from sqlalchemy.orm import Session

from app.core.exceptions import (
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    InvalidTokenTypeError,
    RefreshTokenNotValidError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.repositories.user_repository import UserRepository
from app.schemas.auth import AccessTokenResponse, TokenPairResponse


class AuthService:
    def __init__(self, db: Session, redis: Redis) -> None:
        self.user_repository = UserRepository(db)
        self.redis = redis

    def ensure_seed_user(self, *, email: str, password: str) -> None:
        if self.user_repository.get_by_email(email) is not None:
            return
        self.user_repository.create(
            email=email,
            password_hash=hash_password(password),
        )

    def login(self, *, email: str, password: str) -> TokenPairResponse:
        user = self.user_repository.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        access_token, access_expires_at = create_access_token(str(user.id))
        refresh_token, refresh_jti, refresh_expires_at = create_refresh_token(str(user.id))
        refresh_ttl = max(
            int((refresh_expires_at - datetime.now(refresh_expires_at.tzinfo)).total_seconds()),
            1,
        )
        self.redis.setex(self._refresh_key(user.id), refresh_ttl, refresh_jti)

        return TokenPairResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_expires_in=max(
                int((access_expires_at - datetime.now(access_expires_at.tzinfo)).total_seconds()),
                1,
            ),
            refresh_token_expires_in=refresh_ttl,
        )

    def refresh_access_token(self, refresh_token: str) -> AccessTokenResponse:
        try:
            payload = decode_token(refresh_token)
        except jwt.InvalidTokenError as exc:
            raise InvalidRefreshTokenError() from exc

        if payload.get("type") != "refresh":
            raise InvalidTokenTypeError()

        subject = payload.get("sub")
        refresh_jti = payload.get("jti")
        if subject is None or refresh_jti is None:
            raise InvalidRefreshTokenError()

        user = self.user_repository.get_by_id(int(subject))
        stored_jti = self.redis.get(self._refresh_key(int(subject)))
        if user is None or stored_jti != refresh_jti:
            raise RefreshTokenNotValidError()

        access_token, access_expires_at = create_access_token(str(user.id))
        access_ttl = max(
            int((access_expires_at - datetime.now(access_expires_at.tzinfo)).total_seconds()),
            1,
        )
        return AccessTokenResponse(
            access_token=access_token,
            access_token_expires_in=access_ttl,
        )

    @staticmethod
    def _refresh_key(user_id: int) -> str:
        return f"auth:refresh:{user_id}"
