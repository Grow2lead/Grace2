from django.urls import path
from .views import (
    DashboardView, NutritionView, ActivityView, 
    LogMealView, LogActivityView,
    api_log_meal, api_log_activity, LoginView
)


urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('login/', LoginView.as_view(), name='login'),
    path('nutrition/', NutritionView.as_view(), name='nutrition'),
    path('activity/', ActivityView.as_view(), name='activity'),
    path('log-meal/', LogMealView.as_view(), name='log_meal'),
    path('log-activity/', LogActivityView.as_view(), name='log_activity'),
    path('api/log-meal/', api_log_meal, name='api_log_meal'),
    path('api/log-activity/', api_log_activity, name='api_log_activity'),
]

