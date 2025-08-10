from django.urls import path
from .views import (
    DashboardView, NutritionView, ActivityView, 
    LogMealView, LogActivityView, MealsProviderView, ChallengeHubView, CommunityCornersView, ProfileView,
    api_log_meal, api_log_activity, LoginView, BookExpertView
)
from .fitness_views import FitnessCentersView, FitnessCenterDetailView


urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('login/', LoginView.as_view(), name='login'),
    path('nutrition/', NutritionView.as_view(), name='nutrition'),
    path('activity/', ActivityView.as_view(), name='activity'),
    path('meals-provider/', MealsProviderView.as_view(), name='meals_provider'),
    path('challenge-hub/', ChallengeHubView.as_view(), name='challenge_hub'),
    path('community-corner/', CommunityCornersView.as_view(), name='community_corner'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('log-meal/', LogMealView.as_view(), name='log_meal'),
    path('log-activity/', LogActivityView.as_view(), name='log_activity'),
    path('api/log-meal/', api_log_meal, name='api_log_meal'),
    path('api/log-activity/', api_log_activity, name='api_log_activity'),
    
    # Fitness Centers
    path('fitness-centers/', FitnessCentersView.as_view(), name='fitness_centers'),
    path('fitness-centers/<int:center_id>/', FitnessCenterDetailView.as_view(), name='fitness_center_detail'),
    path('book-expert/', BookExpertView.as_view(), name='book_expert'),
]

