from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Food, MealLog
from .serializers import FoodSerializer, MealLogSerializer


class FoodViewSet(viewsets.ModelViewSet):
    queryset = Food.objects.all().order_by('name')
    serializer_class = FoodSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'localized_name_si', 'localized_name_ta']
    ordering_fields = ['name', 'calories']


class MealLogViewSet(viewsets.ModelViewSet):
    serializer_class = MealLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['log_date', 'meal_type']

    def get_queryset(self):
        return MealLog.objects.filter(user=self.request.user)

