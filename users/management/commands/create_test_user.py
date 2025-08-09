from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = 'Create a test user for development'

    def handle(self, *args, **options):
        # Create test user
        username = 'testuser'
        email = 'test@example.com'
        password = 'testpass123'
        
        try:
            user = User.objects.get(username=username)
            self.stdout.write(
                self.style.WARNING(f'Test user "{username}" already exists')
            )
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                display_name='Test User',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created test user: {username}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Test user credentials:')
        )
        self.stdout.write(f'  Username: {username}')
        self.stdout.write(f'  Password: {password}')
        self.stdout.write(f'  Email: {email}')
        self.stdout.write(
            self.style.SUCCESS('You can now log in with these credentials!')
        )
