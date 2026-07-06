import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from apps.users.models import User

if not User.objects.filter(email="admin@smartchain.com").exists():
    User.objects.create_superuser(
        username="admin",
        email="admin@smartchain.com",
        password="Admin1234!",
        role="admin",
    )
    print("Superuser created → email: admin@smartchain.com  password: Admin1234!")
else:
    print("Superuser already exists.")
