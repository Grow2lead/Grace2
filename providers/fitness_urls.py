from django.urls import path
from . import fitness_views

urlpatterns = [
    # Fitness Center endpoints
    path('fitness-centers/', fitness_views.FitnessCenterListView.as_view(), name='fitness-center-list'),
    path('fitness-centers/<int:id>/', fitness_views.FitnessCenterDetailView.as_view(), name='fitness-center-detail'),
    path('fitness-centers/stats/', fitness_views.fitness_center_stats, name='fitness-center-stats'),
    path('fitness-centers/types/', fitness_views.fitness_center_types, name='fitness-center-types'),
    path('fitness-centers/nearby/', fitness_views.nearby_fitness_centers, name='nearby-fitness-centers'),
    path('fitness-centers/search/', fitness_views.search_fitness_centers, name='search-fitness-centers'),
    
    # Instructor endpoints
    path('fitness-centers/<int:fitness_center_id>/instructors/', 
         fitness_views.FitnessInstructorListView.as_view(), name='fitness-instructors'),
    
    # Class schedule endpoints
    path('fitness-centers/<int:fitness_center_id>/schedules/', 
         fitness_views.FitnessClassScheduleListView.as_view(), name='fitness-class-schedules'),
    
    # Membership endpoints
    path('my-memberships/', fitness_views.UserFitnessMembershipsView.as_view(), name='user-fitness-memberships'),
]
