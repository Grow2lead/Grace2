from rest_framework import serializers
from .models import Food, MealLog


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = '__all__'


class MealLogSerializer(serializers.ModelSerializer):
    food_detail = FoodSerializer(source='food', read_only=True)

    class Meta:
        model = MealLog
        fields = [
            'id', 'user', 'food', 'food_detail', 'quantity', 'meal_type',
            'logged_at', 'log_date'
        ]
        read_only_fields = ['id', 'logged_at', 'user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

