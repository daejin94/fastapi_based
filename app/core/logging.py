import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from app.core.config import Settings


LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
LOG_FILE_NAME = "app.log"


def _resolve_log_level(log_level: str) -> int:
    resolved = getattr(logging, log_level.upper(), logging.INFO)
    if isinstance(resolved, int):
        return resolved
    return logging.INFO


def configure_logging(settings: Settings) -> logging.Logger:
    log_dir = settings.app_log_dir_path
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("app")
    logger.setLevel(_resolve_log_level(settings.app_log_level))
    logger.propagate = False

    log_file = log_dir / LOG_FILE_NAME
    if _has_configured_handler(logger, log_file):
        return logger

    handler = TimedRotatingFileHandler(
        filename=log_file,
        when="midnight",
        interval=1,
        backupCount=settings.app_log_backup_count,
        encoding="utf-8",
    )
    handler.setLevel(_resolve_log_level(settings.app_log_level))
    handler.setFormatter(logging.Formatter(LOG_FORMAT))

    logger.handlers.clear()
    logger.addHandler(handler)
    return logger


def _has_configured_handler(logger: logging.Logger, log_file: Path) -> bool:
    for handler in logger.handlers:
        if not isinstance(handler, TimedRotatingFileHandler):
            continue
        if Path(handler.baseFilename) == log_file:
            return True
    return False
