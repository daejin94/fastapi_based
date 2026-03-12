from time import perf_counter
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.api.v1.api import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.db.session import SessionLocal, init_db
from app.dependencies.redis import create_redis_client
from app.schemas.common import APIResponse
from app.services.auth_service import AuthService


settings = get_settings()
logger = configure_logging(settings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup initiated.")
    init_db()
    db = SessionLocal()
    try:
        redis_client = create_redis_client()
        AuthService(db, redis_client).ensure_seed_user(
            email=settings.seed_user_email.strip().lower(),
            password=settings.seed_user_password,
        )
        app.state.redis = redis_client
        logger.info("Application startup complete.")
        yield
    finally:
        db.close()
        if hasattr(app.state, "redis"):
            app.state.redis.close()
        logger.info("Application shutdown complete.")


app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    lifespan=lifespan,
)
register_exception_handlers(app)
app.include_router(api_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    started_at = perf_counter()
    response = await call_next(request)
    duration_ms = (perf_counter() - started_at) * 1000
    client_host = request.client.host if request.client else "unknown"
    logging_logger = logger.getChild("request")
    logging_logger.info(
        "Request completed | method=%s path=%s status=%s client=%s duration_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        client_host,
        duration_ms,
    )
    return response


@app.get("/", response_model=APIResponse[dict[str, str]])
async def health_check() -> APIResponse[dict[str, str]]:
    return APIResponse(data={"status": "ok"})
