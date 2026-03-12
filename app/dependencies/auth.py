from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationRequiredError
from app.db.session import get_db
from app.models.user import User
from app.services.auth_service import AuthService


bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthenticationRequiredError()

    service = AuthService(db, redis=None)
    return service.get_current_user(credentials.credentials)
