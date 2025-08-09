from rest_framework import serializers
from .models import UserProfile, RecommendationEngine, PersonalizationSettings

class UserProfileSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()
    bmi = serializers.ReadOnlyField()
    bmi_category = serializers.ReadOnlyField()
    profile_completion_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'date_of_birth', 'gender', 'height_cm', 'current_weight_kg', 
            'target_weight_kg', 'activity_level', 'health_goals', 'dietary_restrictions',
            'medical_conditions', 'allergies', 'preferred_meal_times', 'preferred_cuisines',
            'fitness_preferences', 'profile_visibility', 'data_sharing_consent',
            'marketing_consent', 'preferred_language', 'timezone', 
            'profile_completion_percentage', 'age', 'bmi', 'bmi_category',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'profile_completion_percentage', 'age', 'bmi', 'bmi_category']

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Simplified serializer for updating profile"""
    
    class Meta:
        model = UserProfile
        fields = [
            'date_of_birth', 'gender', 'height_cm', 'current_weight_kg', 
            'target_weight_kg', 'activity_level', 'health_goals', 'dietary_restrictions',
            'medical_conditions', 'allergies', 'preferred_meal_times', 'preferred_cuisines',
            'fitness_preferences', 'profile_visibility', 'data_sharing_consent',
            'marketing_consent', 'preferred_language', 'timezone'
        ]

class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendationEngine
        fields = ['id', 'recommendation_type', 'recommendation_data', 'confidence_score', 'created_at']
        read_only_fields = ['id', 'created_at']

class PersonalizationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalizationSettings
        fields = [
            'id', 'enable_meal_reminders', 'enable_activity_reminders', 
            'enable_goal_notifications', 'enable_weekly_summaries',
            'show_meal_recommendations', 'show_activity_recommendations',
            'recommendation_frequency', 'preferred_units', 'dashboard_layout',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
