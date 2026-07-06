"""Celery application configuration."""
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("smart_supply_chain")

# Namespace all Celery config keys with CELERY_ in Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all installed INSTALLED_APPS
app.autodiscover_tasks()
