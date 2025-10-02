import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "primekeralacruise.settings")
django.setup()

from django.contrib.auth.models import User

USERNAME = "admin"
EMAIL = "admin@gamil.com"
PASSWORD = "admin"

if not User.objects.filter(username=USERNAME).exists():
    User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
    print("Superuser created!")
else:
    print("Superuser already exists!")