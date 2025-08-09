from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    display_name = models.CharField(max_length=120, blank=True)
    language_preference = models.CharField(
        max_length=5,
        choices=(('en', 'English'), ('si', 'Sinhala'), ('ta', 'Tamil')),
        default='en',
    )

    def __str__(self) -> str:
        return self.username

