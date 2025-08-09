from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FoodViewSet, MealLogViewSet


router = DefaultRouter()
router.register(r'foods', FoodViewSet, basename='food')
router.register(r'meal-logs', MealLogViewSet, basename='meal-log')


urlpatterns = [
    path('', include(router.urls)),
]

