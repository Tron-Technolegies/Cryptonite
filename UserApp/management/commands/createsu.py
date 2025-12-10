import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Create a superuser using environment variables (safe for Render)"

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not username or not email or not password:
            self.stdout.write(self.style.ERROR(
                "Missing DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL or DJANGO_SUPERUSER_PASSWORD"
            ))
            return

        # Check if user already exists (search by email)
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.SUCCESS("Superuser already exists."))
            return

        # Create superuser
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        # Make sure superuser is active
        user.is_active = True
        user.save()

        self.stdout.write(self.style.SUCCESS("Superuser created successfully."))
