# Load Celery app so shared_task works everywhere.
# Wrapped in try/except so the project starts without Celery installed (local SQLite dev).
try:
    from .celery import app as celery_app  # noqa: F401
    __all__ = ["celery_app"]
except ImportError:
    pass
