from django.conf import settings
from django.db import models


class Food(models.Model):
    name = models.CharField(max_length=200)
    localized_name_si = models.CharField(max_length=200, blank=True)
    localized_name_ta = models.CharField(max_length=200, blank=True)
    serving_size_grams = models.PositiveIntegerField(default=100)
    calories = models.FloatField()
    protein_g = models.FloatField(default=0)
    carbs_g = models.FloatField(default=0)
    fat_g = models.FloatField(default=0)

    def __str__(self) -> str:
        return self.name


class MealLog(models.Model):
    MEAL_TYPES = (
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.FloatField(help_text="Multiplier of serving size")
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    logged_at = models.DateTimeField(auto_now_add=True)
    log_date = models.DateField()

    class Meta:
        ordering = ['-logged_at']


