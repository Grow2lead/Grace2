from rest_framework import serializers
from .models import (
    Provider, FitnessCenter, FitnessInstructor, 
    FitnessClassSchedule, FitnessMembership, ProviderService
)

class FitnessInstructorSerializer(serializers.ModelSerializer):
    """Serializer for fitness instructors"""
    
    class Meta:
        model = FitnessInstructor
        fields = [
            'id', 'name', 'name_si', 'name_ta', 'specializations',
            'bio', 'certifications', 'years_experience', 'available_days',
            'hourly_rate', 'email', 'phone', 'average_rating', 'total_reviews',
            'is_active'
        ]

class FitnessClassScheduleSerializer(serializers.ModelSerializer):
    """Serializer for fitness class schedules"""
    instructor = FitnessInstructorSerializer(read_only=True)
    instructor_id = serializers.IntegerField(write_only=True)
    weekday_display = serializers.CharField(source='get_weekday_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_level_display', read_only=True)
    
    class Meta:
        model = FitnessClassSchedule
        fields = [
            'id', 'instructor', 'instructor_id', 'service', 'class_name',
            'description', 'difficulty_level', 'difficulty_display',
            'weekday', 'weekday_display', 'start_time', 'end_time',
            'max_participants', 'drop_in_price', 'package_price',
            'package_sessions', 'is_active'
        ]

class FitnessCenterDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for fitness centers"""
    provider = serializers.StringRelatedField(read_only=True)
    fitness_type_display = serializers.CharField(source='get_fitness_type_display', read_only=True)
    instructors = FitnessInstructorSerializer(many=True, read_only=True)
    class_schedules = FitnessClassScheduleSerializer(many=True, read_only=True)
    
    # Provider details
    business_name = serializers.CharField(source='provider.business_name', read_only=True)
    business_name_si = serializers.CharField(source='provider.business_name_si', read_only=True)
    business_name_ta = serializers.CharField(source='provider.business_name_ta', read_only=True)
    address = serializers.CharField(source='provider.address', read_only=True)
    city = serializers.CharField(source='provider.city', read_only=True)
    district = serializers.CharField(source='provider.district', read_only=True)
    phone = serializers.CharField(source='provider.phone', read_only=True)
    email = serializers.EmailField(source='provider.email', read_only=True)
    website = serializers.URLField(source='provider.website', read_only=True)
    latitude = serializers.DecimalField(source='provider.latitude', max_digits=9, decimal_places=6, read_only=True)
    longitude = serializers.DecimalField(source='provider.longitude', max_digits=9, decimal_places=6, read_only=True)
    operating_hours = serializers.JSONField(source='provider.operating_hours', read_only=True)
    amenities = serializers.JSONField(source='provider.amenities', read_only=True)
    average_rating = serializers.DecimalField(source='provider.average_rating', max_digits=3, decimal_places=2, read_only=True)
    total_reviews = serializers.IntegerField(source='provider.total_reviews', read_only=True)
    is_verified = serializers.BooleanField(source='provider.is_verified', read_only=True)
    
    class Meta:
        model = FitnessCenter
        fields = [
            'id', 'provider', 'fitness_type', 'fitness_type_display',
            'business_name', 'business_name_si', 'business_name_ta',
            'address', 'city', 'district', 'phone', 'email', 'website',
            'latitude', 'longitude', 'operating_hours', 'amenities',
            'average_rating', 'total_reviews', 'is_verified',
            'total_area_sqft', 'max_capacity', 'parking_spaces',
            'available_equipment', 'has_air_conditioning', 'has_shower_facilities',
            'has_locker_rooms', 'has_changing_rooms', 'has_parking', 'has_water_station',
            'membership_types', 'trial_class_available', 'trial_class_price',
            'group_classes_available', 'personal_training_available',
            'nutritionist_available', 'physiotherapist_available', 'massage_therapy_available',
            'min_age', 'kids_programs_available', 'senior_programs_available',
            'covid_safety_measures', 'first_aid_certified_staff',
            'early_morning_access', 'late_night_access', 'twenty_four_seven',
            'instructors', 'class_schedules'
        ]

class FitnessCenterListSerializer(serializers.ModelSerializer):
    """List serializer for fitness centers"""
    provider = serializers.StringRelatedField(read_only=True)
    fitness_type_display = serializers.CharField(source='get_fitness_type_display', read_only=True)
    
    # Provider details
    business_name = serializers.CharField(source='provider.business_name', read_only=True)
    business_name_si = serializers.CharField(source='provider.business_name_si', read_only=True)
    address = serializers.CharField(source='provider.address', read_only=True)
    city = serializers.CharField(source='provider.city', read_only=True)
    district = serializers.CharField(source='provider.district', read_only=True)
    latitude = serializers.DecimalField(source='provider.latitude', max_digits=9, decimal_places=6, read_only=True)
    longitude = serializers.DecimalField(source='provider.longitude', max_digits=9, decimal_places=6, read_only=True)
    average_rating = serializers.DecimalField(source='provider.average_rating', max_digits=3, decimal_places=2, read_only=True)
    total_reviews = serializers.IntegerField(source='provider.total_reviews', read_only=True)
    is_verified = serializers.BooleanField(source='provider.is_verified', read_only=True)
    
    # Convenience fields
    instructor_count = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    
    class Meta:
        model = FitnessCenter
        fields = [
            'id', 'provider', 'fitness_type', 'fitness_type_display',
            'business_name', 'business_name_si', 'address', 'city', 'district',
            'latitude', 'longitude', 'average_rating', 'total_reviews', 'is_verified',
            'max_capacity', 'trial_class_available', 'trial_class_price',
            'group_classes_available', 'personal_training_available',
            'instructor_count', 'distance'
        ]
    
    def get_instructor_count(self, obj):
        return obj.instructors.filter(is_active=True).count()
    
    def get_distance(self, obj):
        # This would be calculated based on user's location
        # For now, return None - can be enhanced with geolocation
        return None

class FitnessMembershipSerializer(serializers.ModelSerializer):
    """Serializer for fitness memberships"""
    fitness_center = FitnessCenterListSerializer(read_only=True)
    fitness_center_id = serializers.IntegerField(write_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_active_membership = serializers.BooleanField(source='is_active', read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = FitnessMembership
        fields = [
            'id', 'fitness_center', 'fitness_center_id', 'membership_type',
            'start_date', 'end_date', 'status', 'status_display',
            'amount_paid', 'payment_method', 'total_visits', 'last_visit',
            'auto_renewal', 'is_active_membership', 'days_remaining',
            'created_at'
        ]

class FitnessSearchSerializer(serializers.Serializer):
    """Serializer for fitness center search parameters"""
    fitness_type = serializers.ChoiceField(
        choices=FitnessCenter.FITNESS_TYPE_CHOICES,
        required=False
    )
    district = serializers.ChoiceField(
        choices=Provider.DISTRICT_CHOICES,
        required=False
    )
    has_parking = serializers.BooleanField(required=False)
    has_shower_facilities = serializers.BooleanField(required=False)
    personal_training_available = serializers.BooleanField(required=False)
    group_classes_available = serializers.BooleanField(required=False)
    trial_class_available = serializers.BooleanField(required=False)
    min_rating = serializers.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        min_value=0, 
        max_value=5, 
        required=False
    )
    max_price = serializers.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        required=False
    )
    latitude = serializers.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        required=False
    )
    longitude = serializers.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        required=False
    )
    radius_km = serializers.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        required=False,
        default=10
    )

