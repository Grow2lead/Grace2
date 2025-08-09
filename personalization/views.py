from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import UserProfile, RecommendationEngine, PersonalizationSettings
from .serializers import (
    UserProfileSerializer, 
    UserProfileUpdateSerializer,
    RecommendationSerializer,
    PersonalizationSettingsSerializer
)

User = get_user_model()

class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """Get or update user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserProfileUpdateSerializer
        return UserProfileSerializer

class PersonalizationSettingsDetailView(generics.RetrieveUpdateAPIView):
    """Get or update personalization settings"""
    serializer_class = PersonalizationSettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        settings, created = PersonalizationSettings.objects.get_or_create(user=self.request.user)
        return settings

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommendations(request):
    """Get personalized recommendations for the user"""
    recommendation_type = request.GET.get('type', 'all')
    
    recommendations = {
        'meal_recommendations': [],
        'activity_recommendations': [],
        'goal_recommendations': []
    }
    
    try:
        if recommendation_type in ['all', 'meal']:
            meal_recs = RecommendationEngine.get_meal_recommendations(request.user)
            recommendations['meal_recommendations'] = meal_recs
        
        if recommendation_type in ['all', 'activity']:
            activity_recs = RecommendationEngine.get_activity_recommendations(request.user)
            recommendations['activity_recommendations'] = activity_recs
        
        if recommendation_type in ['all', 'goal']:
            # Basic goal recommendations
            profile = getattr(request.user, 'profile', None)
            if profile and profile.target_weight_kg and profile.current_weight_kg:
                weight_diff = float(profile.target_weight_kg) - float(profile.current_weight_kg)
                if weight_diff > 0:
                    recommendations['goal_recommendations'] = [{
                        'type': 'weight_gain',
                        'message': f'You need to gain {abs(weight_diff):.1f} kg to reach your target weight',
                        'suggestion': 'Consider increasing your caloric intake with healthy foods'
                    }]
                elif weight_diff < 0:
                    recommendations['goal_recommendations'] = [{
                        'type': 'weight_loss',
                        'message': f'You need to lose {abs(weight_diff):.1f} kg to reach your target weight',
                        'suggestion': 'Consider a balanced diet with regular exercise'
                    }]
                else:
                    recommendations['goal_recommendations'] = [{
                        'type': 'maintain',
                        'message': 'You are at your target weight! Keep up the good work!',
                        'suggestion': 'Focus on maintaining your current healthy habits'
                    }]
        
        return Response({
            'success': True,
            'recommendations': recommendations
        })
    
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_recommendation_shown(request):
    """Mark a recommendation as shown to the user"""
    recommendation_id = request.data.get('recommendation_id')
    
    try:
        recommendation = get_object_or_404(RecommendationEngine, id=recommendation_id, user=request.user)
        recommendation.is_shown = True
        recommendation.save()
        
        return Response({
            'success': True,
            'message': 'Recommendation marked as shown'
        })
    
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_recommendation(request):
    """Mark a recommendation as accepted by the user"""
    recommendation_id = request.data.get('recommendation_id')
    
    try:
        recommendation = get_object_or_404(RecommendationEngine, id=recommendation_id, user=request.user)
        recommendation.is_accepted = True
        recommendation.is_shown = True
        recommendation.save()
        
        return Response({
            'success': True,
            'message': 'Recommendation accepted'
        })
    
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_completion_status(request):
    """Get profile completion status and suggestions"""
    profile = getattr(request.user, 'profile', None)
    
    if not profile:
        return Response({
            'completion_percentage': 0,
            'missing_fields': ['Create your profile to get started'],
            'suggestions': ['Complete your profile to get personalized recommendations']
        })
    
    missing_fields = []
    suggestions = []
    
    if not profile.date_of_birth:
        missing_fields.append('Date of Birth')
        suggestions.append('Add your date of birth for age-specific recommendations')
    
    if not profile.height_cm or not profile.current_weight_kg:
        missing_fields.append('Height/Weight')
        suggestions.append('Add your height and weight to calculate BMI and get better recommendations')
    
    if not profile.health_goals:
        missing_fields.append('Health Goals')
        suggestions.append('Set your health goals to get targeted recommendations')
    
    if not profile.dietary_restrictions:
        missing_fields.append('Dietary Preferences')
        suggestions.append('Add dietary restrictions to filter food recommendations')
    
    if not profile.fitness_preferences:
        missing_fields.append('Fitness Preferences')
        suggestions.append('Add your preferred activities for better workout suggestions')
    
    return Response({
        'completion_percentage': profile.profile_completion_percentage,
        'missing_fields': missing_fields,
        'suggestions': suggestions,
        'profile_stats': {
            'bmi': profile.bmi,
            'bmi_category': profile.bmi_category,
            'age': profile.age
        }
    })