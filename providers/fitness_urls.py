from django.urls import path
from .fitness_views import (
    FitnessCenterListView, FitnessCenterDetailView, FitnessInstructorListView,
    FitnessClassScheduleListView, UserFitnessMembershipsView,
    fitness_center_stats, fitness_center_types, nearby_fitness_centers, search_fitness_centers
)

urlpatterns = [
    # Fitness Center endpoints
    path('fitness-centers/', FitnessCenterListView.as_view(), name='fitness-center-list'),
    path('fitness-centers/<int:id>/', FitnessCenterDetailView.as_view(), name='fitness-center-detail'),
    path('fitness-centers/stats/', fitness_center_stats, name='fitness-center-stats'),
    path('fitness-centers/types/', fitness_center_types, name='fitness-center-types'),
    path('fitness-centers/nearby/', nearby_fitness_centers, name='nearby-fitness-centers'),
    path('fitness-centers/search/', search_fitness_centers, name='search-fitness-centers'),
    
    # Instructor endpoints
    path('fitness-centers/<int:fitness_center_id>/instructors/', 
         FitnessInstructorListView.as_view(), name='fitness-instructors'),
    
    # Class schedule endpoints
    path('fitness-centers/<int:fitness_center_id>/schedules/', 
         FitnessClassScheduleListView.as_view(), name='fitness-class-schedules'),
    
    # Membership endpoints
    path('my-memberships/', UserFitnessMembershipsView.as_view(), name='user-fitness-memberships'),
]
