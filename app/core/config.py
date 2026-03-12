from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8-sig",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="Backend API", alias="APP_NAME")
    app_env: str = Field(default="local", alias="APP_ENV")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    cors_allow_origins_raw: str = Field(default="*", alias="CORS_ALLOW_ORIGINS")
    cors_allow_methods_raw: str = Field(default="*", alias="CORS_ALLOW_METHODS")
    cors_allow_headers_raw: str = Field(default="*", alias="CORS_ALLOW_HEADERS")
    cors_allow_credentials: bool = Field(default=False, alias="CORS_ALLOW_CREDENTIALS")
    app_log_dir: str = Field(default="app/logs", alias="APP_LOG_DIR")
    app_log_level: str = Field(default="INFO", alias="APP_LOG_LEVEL")
    app_log_backup_count: int = Field(default=30, alias="APP_LOG_BACKUP_COUNT")

    database_url: str = Field(
        default="postgresql+psycopg://user:password@localhost:5432/app",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    secret_key: str = Field(default="change_me", alias="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    refresh_token_expire_days: int = Field(
        default=7,
        alias="REFRESH_TOKEN_EXPIRE_DAYS",
    )

    seed_user_email: str = Field(
        default="admin@example.com",
        alias="SEED_USER_EMAIL",
    )
    seed_user_password: str = Field(
        default="change_me_1234",
        alias="SEED_USER_PASSWORD",
    )

    @property
    def app_log_dir_path(self) -> Path:
        log_dir = Path(self.app_log_dir)
        if log_dir.is_absolute():
            return log_dir

        project_root = Path(__file__).resolve().parents[2]
        return project_root / log_dir

    @property
    def cors_allow_origins(self) -> list[str]:
        return _split_csv(self.cors_allow_origins_raw)

    @property
    def cors_allow_methods(self) -> list[str]:
        return _split_csv(self.cors_allow_methods_raw)

    @property
    def cors_allow_headers(self) -> list[str]:
        return _split_csv(self.cors_allow_headers_raw)


@lru_cache
def get_settings() -> Settings:
    return Settings()


def _split_csv(value: str) -> list[str]:
    items = [item.strip() for item in value.split(",")]
    return [item for item in items if item]
