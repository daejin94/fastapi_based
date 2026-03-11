from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import get_settings
from app.db.session import SessionLocal, init_db
from app.dependencies.redis import create_redis_client
from app.services.auth_service import AuthService


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        redis_client = create_redis_client()
        AuthService(db, redis_client).ensure_seed_user(
            email=settings.seed_user_email.strip().lower(),
            password=settings.seed_user_password,
        )
        app.state.redis = redis_client
        yield
    finally:
        db.close()
        if hasattr(app.state, "redis"):
            app.state.redis.close()


app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    lifespan=lifespan,
)
app.include_router(api_router)


@app.get("/")
def health_check():
    return {"status": "ok"}
