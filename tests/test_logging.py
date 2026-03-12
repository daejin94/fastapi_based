import importlib
import logging
import sys
from pathlib import Path

import httpx
import pytest


class FakeRedis:
    def close(self) -> None:
        return None


def _clear_app_modules() -> None:
    for module_name in list(sys.modules):
        if module_name == "app" or module_name.startswith("app."):
            sys.modules.pop(module_name)


def _build_app_context(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-with-32-plus-bytes")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/15")
    monkeypatch.setenv("SEED_USER_EMAIL", "admin@example.com")
    monkeypatch.setenv("SEED_USER_PASSWORD", "password1234")
    monkeypatch.setenv("APP_DEBUG", "false")
    monkeypatch.setenv("APP_LOG_DIR", str(tmp_path / "logs"))
    monkeypatch.setenv("APP_LOG_LEVEL", "INFO")

    _clear_app_modules()
    fake_redis = FakeRedis()
    app_main = importlib.import_module("app.main")
    monkeypatch.setattr(app_main, "create_redis_client", lambda: fake_redis)

    return app_main.app


async def _create_client(app):
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://testserver")


def _flush_app_loggers() -> None:
    for handler in logging.getLogger("app").handlers:
        if hasattr(handler, "flush"):
            handler.flush()


@pytest.mark.anyio
async def test_request_logging_writes_daily_rotating_file(tmp_path, monkeypatch) -> None:
    app = _build_app_context(tmp_path, monkeypatch)
    log_file = tmp_path / "logs" / "app.log"

    async with app.router.lifespan_context(app):
        async with await _create_client(app) as client:
            response = await client.get("/")

    _flush_app_loggers()

    assert response.status_code == 200
    assert log_file.exists()

    log_contents = log_file.read_text(encoding="utf-8")
    assert "Application startup complete." in log_contents
    assert "Request completed | method=GET path=/ status=200" in log_contents
