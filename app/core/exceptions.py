from collections.abc import Sequence
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppException(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "app_error"
    detail = "Application error."

    def __init__(
        self,
        detail: str | None = None,
        *,
        status_code: int | None = None,
        error_code: str | None = None,
    ) -> None:
        self.detail = detail or self.detail
        self.status_code = status_code or self.status_code
        self.error_code = error_code or self.error_code
        super().__init__(self.detail)


class AuthenticationError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "authentication_error"
    detail = "Authentication failed."


class InvalidCredentialsError(AuthenticationError):
    error_code = "invalid_credentials"
    detail = "Invalid email or password."


class InvalidRefreshTokenError(AuthenticationError):
    error_code = "invalid_refresh_token"
    detail = "Invalid refresh token."


class InvalidTokenTypeError(AuthenticationError):
    error_code = "invalid_token_type"
    detail = "Invalid token type."


class RefreshTokenNotValidError(AuthenticationError):
    error_code = "refresh_token_not_valid"
    detail = "Refresh token is no longer valid."


def _error_response(
    *,
    status_code: int,
    code: str,
    detail: str,
    errors: Sequence[dict[str, Any]] | None = None,
) -> JSONResponse:
    payload: dict[str, Any] = {"code": code, "detail": detail}
    if errors is not None:
        payload["errors"] = list(errors)
    return JSONResponse(status_code=status_code, content=payload)


async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    return _error_response(
        status_code=exc.status_code,
        code=exc.error_code,
        detail=exc.detail,
    )


async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    return _error_response(
        status_code=exc.status_code,
        code="http_error",
        detail=str(exc.detail),
    )


async def validation_exception_handler(
    _: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return _error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        code="validation_error",
        detail="Validation error.",
        errors=exc.errors(),
    )


async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    return _error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="internal_server_error",
        detail="Internal server error.",
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
