import importlib
import sys
from pathlib import Path

import httpx
import pytest


class FakeRedis:
    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    def setex(self, key: str, _: int, value: str) -> None:
        self._store[key] = value

    def get(self, key: str) -> str | None:
        return self._store.get(key)

    def close(self) -> None:
        return None


def _clear_app_modules() -> None:
    for module_name in list(sys.modules):
        if module_name == "app" or module_name.startswith("app."):
            sys.modules.pop(module_name)


def _build_auth_context(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-with-32-plus-bytes")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/15")
    monkeypatch.setenv("SEED_USER_EMAIL", "admin@example.com")
    monkeypatch.setenv("SEED_USER_PASSWORD", "password1234")
    monkeypatch.setenv("APP_DEBUG", "false")
    monkeypatch.setenv("CORS_ALLOW_ORIGINS", "http://localhost:3000")
    monkeypatch.setenv("CORS_ALLOW_METHODS", "GET,POST,OPTIONS")
    monkeypatch.setenv("CORS_ALLOW_HEADERS", "Authorization,Content-Type")
    monkeypatch.setenv("CORS_ALLOW_CREDENTIALS", "false")

    _clear_app_modules()
    fake_redis = FakeRedis()
    app_main = importlib.import_module("app.main")
    monkeypatch.setattr(app_main, "create_redis_client", lambda: fake_redis)

    return app_main.app


async def _create_client(app):
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://testserver")


@pytest.mark.anyio
async def test_login_returns_access_and_refresh_tokens(tmp_path, monkeypatch) -> None:
    app = _build_auth_context(tmp_path, monkeypatch)

    async with app.router.lifespan_context(app):
        async with await _create_client(app) as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={"email": "admin@example.com", "password": "password1234"},
            )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["message"] is None
    assert payload["data"]["access_token"]
    assert payload["data"]["refresh_token"]
    assert payload["data"]["token_type"] == "bearer"
    assert payload["data"]["access_token_expires_in"] > 0
    assert payload["data"]["refresh_token_expires_in"] > 0


@pytest.mark.anyio
async def test_refresh_issues_new_access_token(tmp_path, monkeypatch) -> None:
    app = _build_auth_context(tmp_path, monkeypatch)

    async with app.router.lifespan_context(app):
        async with await _create_client(app) as client:
            login_response = await client.post(
                "/api/v1/auth/login",
                json={"email": "admin@example.com", "password": "password1234"},
            )
            refresh_token = login_response.json()["data"]["refresh_token"]

            refresh_response = await client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": refresh_token},
            )

    assert refresh_response.status_code == 200
    payload = refresh_response.json()
    assert payload["success"] is True
    assert payload["message"] is None
    assert payload["data"]["access_token"]
    assert payload["data"]["token_type"] == "bearer"
    assert payload["data"]["access_token_expires_in"] > 0


@pytest.mark.anyio
async def test_login_returns_global_exception_response_for_invalid_credentials(
    tmp_path,
    monkeypatch,
) -> None:
    app = _build_auth_context(tmp_path, monkeypatch)

    async with app.router.lifespan_context(app):
        async with await _create_client(app) as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={"email": "admin@example.com", "password": "wrong-password"},
            )

    assert response.status_code == 401
    assert response.json() == {
        "code": "invalid_credentials",
        "detail": "Invalid email or password.",
    }


@pytest.mark.anyio
async def test_refresh_rejects_access_token_with_global_exception_response(
    tmp_path,
    monkeypatch,
) -> None:
    app = _build_auth_context(tmp_path, monkeypatch)

    async with app.router.lifespan_context(app):
        async with await _create_client(app) as client:
            login_response = await client.post(
                "/api/v1/auth/login",
                json={"email": "admin@example.com", "password": "password1234"},
            )
            access_token = login_response.json()["data"]["access_token"]

            response = await client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": access_token},
            )

    assert response.status_code == 401
    assert response.json() == {
        "code": "invalid_token_type",
        "detail": "Invalid token type.",
    }


@pytest.mark.anyio
async def test_login_validation_error_uses_global_handler(tmp_path, monkeypatch) -> None:
    app = _build_auth_context(tmp_path, monkeypatch)

    async with app.router.lifespan_context(app):
        async with await _create_client(app) as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={"email": "admin@example.com"},
            )

    payload = response.json()
    assert response.status_code == 422
    assert payload["code"] == "validation_error"
    assert payload["detail"] == "Validation error."
    assert payload["errors"][0]["loc"][-1] == "password"


@pytest.mark.anyio
async def test_cors_allows_configured_origin_preflight(tmp_path, monkeypatch) -> None:
    app = _build_auth_context(tmp_path, monkeypatch)

    async with app.router.lifespan_context(app):
        async with await _create_client(app) as client:
            response = await client.options(
                "/api/v1/auth/login",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Authorization,Content-Type",
                },
            )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "POST" in response.headers["access-control-allow-methods"]


@pytest.mark.anyio
async def test_cors_rejects_unconfigured_origin_preflight(tmp_path, monkeypatch) -> None:
    app = _build_auth_context(tmp_path, monkeypatch)

    async with app.router.lifespan_context(app):
        async with await _create_client(app) as client:
            response = await client.options(
                "/api/v1/auth/login",
                headers={
                    "Origin": "http://evil.example.com",
                    "Access-Control-Request-Method": "POST",
                },
            )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
