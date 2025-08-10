from django.urls import path
from . import views

app_name = 'personalization'

urlpatterns = [
    # User Profile
    path('profile/', views.UserProfileDetailView.as_view(), name='profile-detail'),
    path('profile/completion/', views.profile_completion_status, name='profile-completion'),
    
    # Personalization Settings
    path('settings/', views.PersonalizationSettingsDetailView.as_view(), name='settings-detail'),
    
    # Recommendations
    path('recommendations/', views.get_recommendations, name='recommendations'),
    path('recommendations/shown/', views.mark_recommendation_shown, name='recommendation-shown'),
    path('recommendations/accept/', views.accept_recommendation, name='recommendation-accept'),
]



