"""
Local development settings — uses SQLite so no PostgreSQL install is needed.
Run with:  set DJANGO_SETTINGS_MODULE=config.settings.local
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Pull in everything from base, then override what differs
from .base import *  # noqa: F401, F403

SECRET_KEY = "local-dev-secret-key-not-for-production"

DEBUG = True

ALLOWED_HOSTS = ["*"]

# ── SQLite (zero-config) ──────────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ── CORS ─────────────────────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True

# ── Email (print to console) ──────────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ── Celery (run tasks eagerly so no Redis needed locally) ─────────────────────
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
