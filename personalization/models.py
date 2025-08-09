from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import json

User = get_user_model()

class UserProfile(models.Model):
    """Enhanced user profile for Phase 1 personalization features"""
    
    ACTIVITY_LEVEL_CHOICES = [
        ('sedentary', 'Sedentary (little or no exercise)'),
        ('lightly_active', 'Lightly Active (light exercise 1-3 days/week)'),
        ('moderately_active', 'Moderately Active (moderate exercise 3-5 days/week)'),
        ('very_active', 'Very Active (hard exercise 6-7 days/week)'),
        ('extremely_active', 'Extremely Active (very hard exercise, physical job)'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]
    
    VISIBILITY_CHOICES = [
        ('private', 'Private'),
        ('friends', 'Friends Only'),
        ('public', 'Public'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Basic Information
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                   validators=[MinValueValidator(50), MaxValueValidator(300)])
    current_weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                           validators=[MinValueValidator(20), MaxValueValidator(500)])
    target_weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                          validators=[MinValueValidator(20), MaxValueValidator(500)])
    
    # Health Information
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_LEVEL_CHOICES, default='sedentary')
    health_goals = models.JSONField(default=list, help_text="List of health goals")
    dietary_restrictions = models.JSONField(default=list, help_text="List of dietary restrictions")
    medical_conditions = models.JSONField(default=list, help_text="List of medical conditions")
    allergies = models.JSONField(default=list, help_text="List of allergies")
    
    # Preferences
    preferred_meal_times = models.JSONField(default=dict, help_text="Preferred meal timing")
    preferred_cuisines = models.JSONField(default=list, help_text="Preferred cuisines")
    fitness_preferences = models.JSONField(default=list, help_text="Preferred fitness activities")
    
    # Privacy & Consent
    profile_visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    data_sharing_consent = models.BooleanField(default=False)
    marketing_consent = models.BooleanField(default=False)
    
    # Localization
    preferred_language = models.CharField(max_length=5, default='en', choices=[
        ('en', 'English'),
        ('si', 'Sinhala'),
        ('ta', 'Tamil'),
    ])
    timezone = models.CharField(max_length=50, default='Asia/Colombo')
    
    # Metadata
    profile_completion_percentage = models.IntegerField(default=0,
                                                       validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def age(self):
        """Calculate age from date of birth"""
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    @property
    def bmi(self):
        """Calculate BMI if height and weight are available"""
        if self.height_cm and self.current_weight_kg:
            height_m = float(self.height_cm) / 100
            return round(float(self.current_weight_kg) / (height_m ** 2), 1)
        return None
    
    @property
    def bmi_category(self):
        """Get BMI category"""
        bmi = self.bmi
        if bmi is None:
            return None
        
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal weight"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"
    
    def calculate_profile_completion(self):
        """Calculate profile completion percentage"""
        total_fields = 15
        completed_fields = 0
        
        if self.date_of_birth:
            completed_fields += 1
        if self.gender:
            completed_fields += 1
        if self.height_cm:
            completed_fields += 1
        if self.current_weight_kg:
            completed_fields += 1
        if self.target_weight_kg:
            completed_fields += 1
        if self.activity_level != 'sedentary':
            completed_fields += 1
        if self.health_goals:
            completed_fields += 1
        if self.dietary_restrictions:
            completed_fields += 1
        if self.preferred_meal_times:
            completed_fields += 1
        if self.preferred_cuisines:
            completed_fields += 1
        if self.fitness_preferences:
            completed_fields += 1
        if self.allergies:
            completed_fields += 1
        if self.medical_conditions:
            completed_fields += 1
        if self.preferred_language:
            completed_fields += 1
        if self.data_sharing_consent:
            completed_fields += 1
        
        percentage = round((completed_fields / total_fields) * 100)
        self.profile_completion_percentage = percentage
        return percentage
    
    def save(self, *args, **kwargs):
        """Override save to update completion percentage"""
        self.calculate_profile_completion()
        super().save(*args, **kwargs)


class RecommendationEngine(models.Model):
    """Basic recommendation engine for Phase 1"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recommendation_type = models.CharField(max_length=50, choices=[
        ('meal', 'Meal Recommendation'),
        ('activity', 'Activity Recommendation'),
        ('goal', 'Goal Recommendation'),
    ])
    recommendation_data = models.JSONField(default=dict)
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    is_shown = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recommendation_type} for {self.user.username}"
    
    @classmethod
    def get_meal_recommendations(cls, user):
        """Get meal recommendations based on user profile and history"""
        from nutrition.models import Food, MealLog
        from datetime import date, timedelta
        
        profile = getattr(user, 'profile', None)
        if not profile:
            return []
        
        recommendations = []
        
        # Get recent meals to avoid repetition
        recent_meals = MealLog.objects.filter(
            user=user,
            log_date__gte=date.today() - timedelta(days=7)
        ).values_list('food_id', flat=True)
        
        # Filter foods based on dietary restrictions
        foods = Food.objects.exclude(id__in=recent_meals)
        
        if profile.dietary_restrictions:
            for restriction in profile.dietary_restrictions:
                if restriction.lower() == 'vegetarian':
                    foods = foods.exclude(name__icontains='chicken').exclude(name__icontains='beef').exclude(name__icontains='fish')
                elif restriction.lower() == 'vegan':
                    foods = foods.exclude(name__icontains='milk').exclude(name__icontains='cheese').exclude(name__icontains='egg')
        
        # Get top 5 foods
        for food in foods[:5]:
            recommendations.append({
                'food_id': food.id,
                'food_name': food.name,
                'calories': food.calories,
                'reason': 'Based on your dietary preferences'
            })
        
        return recommendations
    
    @classmethod
    def get_activity_recommendations(cls, user):
        """Get activity recommendations based on user profile"""
        from activity.models import ActivityLog
        from datetime import date, timedelta
        
        profile = getattr(user, 'profile', None)
        if not profile:
            return []
        
        recommendations = []
        
        # Get recent activities
        recent_activities = ActivityLog.objects.filter(
            user=user,
            started_at__gte=date.today() - timedelta(days=7)
        ).values_list('activity_type', flat=True)
        
        # Activity recommendations based on fitness level
        activity_map = {
            'sedentary': ['walking', 'yoga', 'stretching'],
            'lightly_active': ['jogging', 'cycling', 'swimming'],
            'moderately_active': ['running', 'weight_training', 'dancing'],
            'very_active': ['hiit', 'crossfit', 'martial_arts'],
            'extremely_active': ['marathon_training', 'powerlifting', 'competitive_sports']
        }
        
        suggested_activities = activity_map.get(profile.activity_level, ['walking'])
        
        for activity in suggested_activities:
            if activity not in recent_activities:
                recommendations.append({
                    'activity_type': activity,
                    'duration': 30,
                    'reason': f'Suitable for your {profile.get_activity_level_display().lower()}'
                })
        
        return recommendations[:3]


class PersonalizationSettings(models.Model):
    """User preferences for personalization features"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='personalization_settings')
    
    # Notification Preferences
    enable_meal_reminders = models.BooleanField(default=True)
    enable_activity_reminders = models.BooleanField(default=True)
    enable_goal_notifications = models.BooleanField(default=True)
    enable_weekly_summaries = models.BooleanField(default=True)
    
    # Recommendation Preferences
    show_meal_recommendations = models.BooleanField(default=True)
    show_activity_recommendations = models.BooleanField(default=True)
    recommendation_frequency = models.CharField(max_length=20, default='daily', choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('disabled', 'Disabled'),
    ])
    
    # Display Preferences
    preferred_units = models.CharField(max_length=10, default='metric', choices=[
        ('metric', 'Metric (kg, cm)'),
        ('imperial', 'Imperial (lbs, inches)'),
    ])
    dashboard_layout = models.JSONField(default=dict, help_text="Dashboard widget preferences")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Personalization Settings"