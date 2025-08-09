from django.conf import settings
from django.db import models


class ActivityLog(models.Model):
    ACTIVITY_TYPES = (
        ('walk', 'Walk'),
        ('run', 'Run'),
        ('cycle', 'Cycle'),
        ('workout', 'Workout'),
        ('yoga', 'Yoga'),
        ('other', 'Other'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    duration_minutes = models.PositiveIntegerField()
    distance_km = models.FloatField(default=0)
    calories_burned = models.FloatField(default=0)
    started_at = models.DateTimeField()
    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self) -> str:
        return f"{self.user} {self.activity_type} {self.duration_minutes}m"

