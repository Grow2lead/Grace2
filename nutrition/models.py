from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class FoodCategory(models.Model):
    """Phase 1: Food categories for better organization"""
    name = models.CharField(max_length=100, unique=True)
    name_si = models.CharField(max_length=100, blank=True)
    name_ta = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Food Categories"
    
    def __str__(self):
        return self.name


class Food(models.Model):
    """Enhanced food model with Sri Lankan localization"""
    
    ORIGIN_CHOICES = [
        ('local', 'Local Sri Lankan'),
        ('south_asian', 'South Asian'),
        ('international', 'International'),
        ('processed', 'Processed Food'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=200, help_text="English name")
    name_si = models.CharField(max_length=200, blank=True, help_text="Sinhala name")
    name_ta = models.CharField(max_length=200, blank=True, help_text="Tamil name")
    
    # Categorization
    category = models.ForeignKey(FoodCategory, on_delete=models.SET_NULL, null=True, blank=True)
    origin = models.CharField(max_length=20, choices=ORIGIN_CHOICES, default='local')
    region = models.CharField(max_length=100, blank=True, help_text="Specific region in Sri Lanka")
    
    # Serving Information
    serving_size_grams = models.PositiveIntegerField(default=100)
    common_serving_size = models.CharField(max_length=100, blank=True, 
                                          help_text="e.g., 1 cup, 1 slice, 1 piece")
    serving_size_description = models.CharField(max_length=200, blank=True,
                                               help_text="Description of serving size")
    
    # Nutritional Information (per 100g)
    calories = models.FloatField(validators=[MinValueValidator(0)])
    protein_g = models.FloatField(default=0, validators=[MinValueValidator(0)])
    carbs_g = models.FloatField(default=0, validators=[MinValueValidator(0)])
    fat_g = models.FloatField(default=0, validators=[MinValueValidator(0)])
    fiber_g = models.FloatField(default=0, validators=[MinValueValidator(0)])
    sugar_g = models.FloatField(default=0, validators=[MinValueValidator(0)])
    sodium_mg = models.FloatField(default=0, validators=[MinValueValidator(0)])
    
    # Additional Nutrients
    vitamin_c_mg = models.FloatField(default=0, validators=[MinValueValidator(0)])
    calcium_mg = models.FloatField(default=0, validators=[MinValueValidator(0)])
    iron_mg = models.FloatField(default=0, validators=[MinValueValidator(0)])
    
    # Food Properties
    is_vegetarian = models.BooleanField(default=True)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    is_dairy_free = models.BooleanField(default=True)
    
    # Preparation
    preparation_method = models.CharField(max_length=100, blank=True,
                                        help_text="e.g., boiled, fried, raw")
    cooking_instructions = models.TextField(blank=True)
    
    # Additional Information
    description = models.TextField(blank=True)
    health_benefits = models.TextField(blank=True)
    allergen_info = models.JSONField(default=list, help_text="List of allergens")
    
    # Barcode Support
    barcode = models.CharField(max_length=50, blank=True, null=True)
    
    # Metadata
    is_verified = models.BooleanField(default=False, help_text="Verified by nutritionist")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['origin']),
            models.Index(fields=['is_vegetarian']),
            models.Index(fields=['is_vegan']),
        ]
        ordering = ['name']

    def __str__(self) -> str:
        return self.name
    
    def get_localized_name(self, language='en'):
        """Get food name in specified language"""
        if language == 'si' and self.name_si:
            return self.name_si
        elif language == 'ta' and self.name_ta:
            return self.name_ta
        return self.name
    
    @property
    def calories_per_serving(self):
        """Calculate calories per common serving"""
        if self.serving_size_grams:
            return (self.calories * self.serving_size_grams) / 100
        return self.calories
    
    def get_nutrition_per_serving(self):
        """Get all nutrition values per serving"""
        multiplier = self.serving_size_grams / 100
        return {
            'calories': self.calories * multiplier,
            'protein_g': self.protein_g * multiplier,
            'carbs_g': self.carbs_g * multiplier,
            'fat_g': self.fat_g * multiplier,
            'fiber_g': self.fiber_g * multiplier,
            'sugar_g': self.sugar_g * multiplier,
            'sodium_mg': self.sodium_mg * multiplier,
        }


class LocalFoodDatabase(models.Model):
    """Traditional Sri Lankan foods with cultural information"""
    
    food = models.OneToOneField(Food, on_delete=models.CASCADE, related_name='local_info')
    
    # Cultural Information
    traditional_name = models.CharField(max_length=200, help_text="Traditional/cultural name")
    cultural_significance = models.TextField(blank=True)
    traditional_preparation = models.TextField(blank=True)
    ceremonial_use = models.CharField(max_length=200, blank=True)
    
    # Seasonal Information
    seasonal_availability = models.JSONField(default=list, help_text="Available months")
    harvest_season = models.CharField(max_length=100, blank=True)
    
    # Regional Variations
    regional_names = models.JSONField(default=dict, help_text="Names in different regions")
    regional_preparations = models.JSONField(default=dict, help_text="Regional cooking methods")
    
    # Ayurvedic Properties
    ayurvedic_properties = models.JSONField(default=dict, help_text="Ayurvedic categorization")
    medicinal_uses = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Local Food Information"
        verbose_name_plural = "Local Food Information"
    
    def __str__(self):
        return f"Local info for {self.food.name}"


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


