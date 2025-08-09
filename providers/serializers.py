from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Provider, ProviderService, ProviderMedia

User = get_user_model()

class ProviderMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderMedia
        fields = ['id', 'title', 'image', 'is_featured', 'uploaded_at']

class ProviderServiceSerializer(serializers.ModelSerializer):
    localized_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ProviderService
        fields = [
            'id', 'name', 'localized_name', 'service_type', 'description', 
            'price', 'currency', 'duration_minutes', 'max_participants',
            'is_bookable', 'is_active'
        ]
    
    def get_localized_name(self, obj):
        language = self.context.get('request', {}).META.get('HTTP_ACCEPT_LANGUAGE', 'en')[:2]
        if language == 'si' and obj.name_si:
            return obj.name_si
        elif language == 'ta' and obj.name_ta:
            return obj.name_ta
        return obj.name

class ProviderListSerializer(serializers.ModelSerializer):
    """Serializer for provider list view with essential information"""
    localized_name = serializers.SerializerMethodField()
    localized_description = serializers.SerializerMethodField()
    featured_image = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    
    class Meta:
        model = Provider
        fields = [
            'id', 'slug', 'business_name', 'localized_name', 'category', 
            'district', 'city', 'localized_description', 'average_rating', 
            'total_reviews', 'is_verified', 'featured_image', 'distance',
            'latitude', 'longitude'
        ]
    
    def get_localized_name(self, obj):
        language = self.context.get('request', {}).META.get('HTTP_ACCEPT_LANGUAGE', 'en')[:2]
        return obj.get_localized_name(language)
    
    def get_localized_description(self, obj):
        language = self.context.get('request', {}).META.get('HTTP_ACCEPT_LANGUAGE', 'en')[:2]
        description = obj.get_localized_description(language)
        # Truncate for list view
        return description[:200] + '...' if len(description) > 200 else description
    
    def get_featured_image(self, obj):
        featured_media = obj.media.filter(is_featured=True).first()
        if featured_media and featured_media.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(featured_media.image.url)
        return None
    
    def get_distance(self, obj):
        # This would be calculated based on user's location
        # For now, return None - will be implemented in search view
        return None

class ProviderDetailSerializer(serializers.ModelSerializer):
    """Detailed provider information for detail view"""
    localized_name = serializers.SerializerMethodField()
    localized_description = serializers.SerializerMethodField()
    services = ProviderServiceSerializer(many=True, read_only=True)
    media = ProviderMediaSerializer(many=True, read_only=True)
    rating_distribution = serializers.SerializerMethodField()
    
    class Meta:
        model = Provider
        fields = [
            'id', 'slug', 'business_name', 'localized_name', 'category', 
            'subcategory', 'district', 'city', 'address', 'phone', 'email',
            'whatsapp', 'website', 'description', 'localized_description',
            'operating_hours', 'amenities', 'pricing_info', 'is_verified',
            'average_rating', 'total_reviews', 'total_bookings', 
            'accepts_online_bookings', 'cancellation_policy',
            'latitude', 'longitude', 'services', 'media', 'rating_distribution',
            'created_at'
        ]
    
    def get_localized_name(self, obj):
        language = self.context.get('request', {}).META.get('HTTP_ACCEPT_LANGUAGE', 'en')[:2]
        return obj.get_localized_name(language)
    
    def get_localized_description(self, obj):
        language = self.context.get('request', {}).META.get('HTTP_ACCEPT_LANGUAGE', 'en')[:2]
        return obj.get_localized_description(language)
    
    def get_rating_distribution(self, obj):
        # This would calculate actual rating distribution
        # For now, return a sample distribution
        return {
            '5': 60,
            '4': 25,
            '3': 10,
            '2': 3,
            '1': 2
        }

class ProviderRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for provider registration"""
    services = serializers.JSONField(write_only=True, required=False)
    
    class Meta:
        model = Provider
        fields = [
            'business_name', 'business_name_si', 'business_name_ta',
            'category', 'subcategory', 'email', 'phone', 'whatsapp', 'website',
            'address', 'city', 'district', 'postal_code', 'latitude', 'longitude',
            'description', 'description_si', 'description_ta',
            'operating_hours', 'amenities', 'pricing_info', 'cancellation_policy',
            'accepts_online_bookings', 'services'
        ]
    
    def create(self, validated_data):
        services_data = validated_data.pop('services', [])
        user = self.context['request'].user
        
        # Create provider
        provider = Provider.objects.create(user=user, **validated_data)
        
        # Create services
        for service_data in services_data:
            ProviderService.objects.create(provider=provider, **service_data)
        
        return provider

class ProviderUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating provider information"""
    
    class Meta:
        model = Provider
        fields = [
            'business_name', 'business_name_si', 'business_name_ta',
            'subcategory', 'phone', 'whatsapp', 'website',
            'address', 'city', 'district', 'postal_code', 'latitude', 'longitude',
            'description', 'description_si', 'description_ta',
            'operating_hours', 'amenities', 'pricing_info', 'cancellation_policy',
            'accepts_online_bookings'
        ]
        
    def update(self, instance, validated_data):
        # Update all fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class ProviderServiceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new services"""
    
    class Meta:
        model = ProviderService
        fields = [
            'name', 'name_si', 'name_ta', 'service_type', 'description',
            'price', 'duration_minutes', 'max_participants', 'is_bookable'
        ]
    
    def create(self, validated_data):
        provider = self.context['provider']
        return ProviderService.objects.create(provider=provider, **validated_data)

class ProviderSearchSerializer(serializers.ModelSerializer):
    """Optimized serializer for search results"""
    localized_name = serializers.SerializerMethodField()
    featured_image = serializers.SerializerMethodField()
    starting_price = serializers.SerializerMethodField()
    distance = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = Provider
        fields = [
            'id', 'slug', 'business_name', 'localized_name', 'category',
            'district', 'city', 'average_rating', 'total_reviews', 
            'is_verified', 'featured_image', 'starting_price', 'distance',
            'latitude', 'longitude'
        ]
    
    def get_localized_name(self, obj):
        language = self.context.get('request', {}).META.get('HTTP_ACCEPT_LANGUAGE', 'en')[:2]
        return obj.get_localized_name(language)
    
    def get_featured_image(self, obj):
        featured_media = obj.media.filter(is_featured=True).first()
        if featured_media and featured_media.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(featured_media.image.url)
        return None
    
    def get_starting_price(self, obj):
        min_price_service = obj.services.filter(is_active=True).order_by('price').first()
        return min_price_service.price if min_price_service else None

