"""Development settings."""
from .base import *  # noqa: F401, F403
from pathlib import Path

DEBUG = True

ALLOWED_HOSTS = ["*"]

CORS_ALLOW_ALL_ORIGINS = True

# Use SQLite for local development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Use Django's built-in email backend during development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
