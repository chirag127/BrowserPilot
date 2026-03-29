"""Structured logging configuration."""

import logging
import sys
import time
from contextlib import contextmanager
from typing import Any

import structlog


def configure_logging(level: str = "INFO") -> None:
    """Configure structured logging with JSON and console renderers."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.UnicodeDecoder(),
            _get_renderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    stdlib_handler = logging.StreamHandler(sys.stdout)
    stdlib_handler.setFormatter(logging.Formatter("%(message)s"))

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(stdlib_handler)
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))


def _get_renderer() -> Any:
    """Select renderer based on TTY."""
    if sys.stdout.isatty():
        return structlog.dev.ConsoleRenderer(colors=True)
    return structlog.processors.JSONRenderer()


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


@contextmanager
def log_timing(logger: structlog.stdlib.BoundLogger, event: str, **kwargs: Any):
    """Context manager that logs elapsed time for a block."""
    start = time.monotonic()
    logger.info(event, **kwargs)
    try:
        yield
    finally:
        elapsed = time.monotonic() - start
        logger.info(
            f"{event}_complete",
            elapsed_seconds=round(elapsed, 3),
            **kwargs,
        )
