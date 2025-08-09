from django.contrib import admin
from .models import UserProfile, RecommendationEngine, PersonalizationSettings

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'gender', 'activity_level', 'profile_completion_percentage', 'created_at')
    list_filter = ('gender', 'activity_level', 'preferred_language', 'profile_visibility')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('profile_completion_percentage', 'created_at', 'updated_at', 'age', 'bmi', 'bmi_category')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Basic Information', {
            'fields': ('date_of_birth', 'gender', 'height_cm', 'current_weight_kg', 'target_weight_kg')
        }),
        ('Health Information', {
            'fields': ('activity_level', 'health_goals', 'dietary_restrictions', 'medical_conditions', 'allergies')
        }),
        ('Preferences', {
            'fields': ('preferred_meal_times', 'preferred_cuisines', 'fitness_preferences')
        }),
        ('Privacy & Consent', {
            'fields': ('profile_visibility', 'data_sharing_consent', 'marketing_consent')
        }),
        ('Localization', {
            'fields': ('preferred_language', 'timezone')
        }),
        ('Metadata', {
            'fields': ('profile_completion_percentage', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Calculated Fields', {
            'fields': ('age', 'bmi', 'bmi_category'),
            'classes': ('collapse',)
        }),
    )

@admin.register(RecommendationEngine)
class RecommendationEngineAdmin(admin.ModelAdmin):
    list_display = ('user', 'recommendation_type', 'confidence_score', 'is_shown', 'is_accepted', 'created_at')
    list_filter = ('recommendation_type', 'is_shown', 'is_accepted')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)

@admin.register(PersonalizationSettings)
class PersonalizationSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'enable_meal_reminders', 'enable_activity_reminders', 'recommendation_frequency')
    list_filter = ('enable_meal_reminders', 'enable_activity_reminders', 'recommendation_frequency', 'preferred_units')
    search_fields = ('user__username',)