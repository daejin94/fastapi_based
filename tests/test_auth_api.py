import importlib
import sys
from pathlib import Path

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
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/15")
    monkeypatch.setenv("SEED_USER_EMAIL", "admin@example.com")
    monkeypatch.setenv("SEED_USER_PASSWORD", "password1234")

    _clear_app_modules()
    importlib.import_module("app.main")
    auth_router = importlib.import_module("app.api.v1.routers.auth")
    fake_redis = FakeRedis()

    from app.db.session import SessionLocal, init_db
    from app.services.auth_service import AuthService

    init_db()
    db = SessionLocal()
    try:
        AuthService(db, fake_redis).ensure_seed_user(
            email="admin@example.com",
            password="password1234",
        )
        return auth_router, db, fake_redis
    except Exception:
        db.close()
        raise


def test_login_returns_access_and_refresh_tokens(tmp_path, monkeypatch) -> None:
    auth_router, db, redis = _build_auth_context(tmp_path, monkeypatch)
    try:
        response = auth_router.login(
            payload=auth_router.LoginRequest(
                email="admin@example.com",
                password="password1234",
            ),
            db=db,
            redis=redis,
        )
    finally:
        db.close()

    assert response.access_token
    assert response.refresh_token
    assert response.token_type == "bearer"
    assert response.access_token_expires_in > 0
    assert response.refresh_token_expires_in > 0


def test_refresh_issues_new_access_token(tmp_path, monkeypatch) -> None:
    auth_router, db, redis = _build_auth_context(tmp_path, monkeypatch)
    try:
        login_response = auth_router.login(
            payload=auth_router.LoginRequest(
                email="admin@example.com",
                password="password1234",
            ),
            db=db,
            redis=redis,
        )
        refresh_token = login_response.refresh_token

        refresh_response = auth_router.refresh_access_token(
            payload=auth_router.RefreshTokenRequest(refresh_token=refresh_token),
            db=db,
            redis=redis,
        )
    finally:
        db.close()

    assert refresh_response.access_token
    assert refresh_response.token_type == "bearer"
    assert refresh_response.access_token_expires_in > 0


def test_refresh_rejects_access_token(tmp_path, monkeypatch) -> None:
    auth_router, db, redis = _build_auth_context(tmp_path, monkeypatch)
    try:
        login_response = auth_router.login(
            payload=auth_router.LoginRequest(
                email="admin@example.com",
                password="password1234",
            ),
            db=db,
            redis=redis,
        )
        access_token = login_response.access_token

        try:
            auth_router.refresh_access_token(
                payload=auth_router.RefreshTokenRequest(refresh_token=access_token),
                db=db,
                redis=redis,
            )
            raised = None
        except Exception as exc:
            raised = exc
    finally:
        db.close()

    assert raised.status_code == 401
    assert raised.detail == "Invalid token type."
