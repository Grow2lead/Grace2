from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Booking, BookingAvailability, BookingCancellation, BookingPayment
from providers.serializers import ProviderListSerializer, ProviderServiceSerializer

User = get_user_model()

class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new bookings"""
    
    class Meta:
        model = Booking
        fields = [
            'provider', 'service', 'booking_date', 'booking_time', 
            'participants', 'customer_name', 'customer_phone', 
            'customer_email', 'special_requests'
        ]
    
    def validate(self, data):
        """Validate booking data"""
        from .services import BookingService
        
        # Check availability
        booking_service = BookingService()
        is_available, message = booking_service.check_availability(
            provider=data['provider'],
            service=data['service'],
            date=data['booking_date'],
            time=data['booking_time'],
            participants=data['participants']
        )
        
        if not is_available:
            raise serializers.ValidationError({'booking_time': message})
        
        return data
    
    def create(self, validated_data):
        """Create booking with proper initialization"""
        user = self.context['request'].user
        service = validated_data['service']
        
        # Set pricing and duration from service
        validated_data['user'] = user
        validated_data['service_price'] = service.price
        validated_data['duration_minutes'] = service.duration_minutes
        validated_data['total_amount'] = service.price * validated_data['participants']
        
        return Booking.objects.create(**validated_data)

class BookingListSerializer(serializers.ModelSerializer):
    """Serializer for booking list view"""
    provider_name = serializers.CharField(source='provider.business_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    can_cancel = serializers.BooleanField(read_only=True)
    can_reschedule = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'booking_id', 'provider_name', 'service_name', 'booking_date', 
            'booking_time', 'duration_minutes', 'participants', 'status', 
            'payment_status', 'total_amount', 'can_cancel', 'can_reschedule', 
            'created_at'
        ]

class BookingDetailSerializer(serializers.ModelSerializer):
    """Detailed booking information"""
    provider = ProviderListSerializer(read_only=True)
    service = ProviderServiceSerializer(read_only=True)
    can_cancel = serializers.BooleanField(read_only=True)
    can_reschedule = serializers.BooleanField(read_only=True)
    booking_datetime = serializers.DateTimeField(read_only=True)
    end_datetime = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'booking_id', 'provider', 'service', 'booking_date', 'booking_time',
            'booking_datetime', 'end_datetime', 'duration_minutes', 'participants',
            'status', 'payment_status', 'service_price', 'total_amount', 'currency',
            'customer_name', 'customer_phone', 'customer_email', 'special_requests',
            'provider_notes', 'can_cancel', 'can_reschedule', 'reschedule_count',
            'reminder_sent', 'confirmation_sent', 'created_at', 'updated_at'
        ]

class BookingUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating booking details"""
    
    class Meta:
        model = Booking
        fields = [
            'customer_name', 'customer_phone', 'customer_email', 'special_requests'
        ]

class BookingCancellationSerializer(serializers.ModelSerializer):
    """Serializer for booking cancellations"""
    
    class Meta:
        model = BookingCancellation
        fields = ['cancellation_type', 'reason']
    
    def create(self, validated_data):
        booking = self.context['booking']
        user = self.context['request'].user
        
        # Determine cancellation type
        if user == booking.user:
            validated_data['cancellation_type'] = 'customer'
        elif hasattr(user, 'provider_profile') and user.provider_profile == booking.provider:
            validated_data['cancellation_type'] = 'provider'
        else:
            validated_data['cancellation_type'] = 'system'
        
        validated_data['booking'] = booking
        validated_data['cancelled_by'] = user
        
        return BookingCancellation.objects.create(**validated_data)

class AvailabilitySlotSerializer(serializers.ModelSerializer):
    """Serializer for availability slots"""
    available_spots = serializers.IntegerField(read_only=True)
    is_fully_booked = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = BookingAvailability
        fields = [
            'id', 'date', 'start_time', 'end_time', 'max_bookings', 
            'current_bookings', 'available_spots', 'is_available', 
            'is_blocked', 'is_fully_booked'
        ]

class BookingPaymentSerializer(serializers.ModelSerializer):
    """Serializer for payment information"""
    
    class Meta:
        model = BookingPayment
        fields = [
            'id', 'payment_method', 'amount', 'currency', 'status',
            'gateway_transaction_id', 'processed_at', 'created_at'
        ]
        read_only_fields = ['id', 'gateway_transaction_id', 'processed_at', 'created_at']

class RescheduleBookingSerializer(serializers.Serializer):
    """Serializer for rescheduling bookings"""
    new_booking_date = serializers.DateField()
    new_booking_time = serializers.TimeField()
    reason = serializers.CharField(max_length=500, required=False)
    
    def validate(self, data):
        """Validate reschedule data"""
        booking = self.context['booking']
        
        # Check if booking can be rescheduled
        if not booking.can_reschedule:
            raise serializers.ValidationError('This booking cannot be rescheduled.')
        
        # Check new slot availability
        from .services import BookingService
        booking_service = BookingService()
        is_available, message = booking_service.check_availability(
            provider=booking.provider,
            service=booking.service,
            date=data['new_booking_date'],
            time=data['new_booking_time'],
            participants=booking.participants,
            exclude_booking=booking
        )
        
        if not is_available:
            raise serializers.ValidationError({'new_booking_time': message})
        
        return data

class ProviderBookingsSerializer(serializers.ModelSerializer):
    """Serializer for provider's booking management"""
    customer_name = serializers.CharField(source='customer_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'booking_id', 'customer_name', 'service_name', 'booking_date',
            'booking_time', 'duration_minutes', 'participants', 'status',
            'payment_status', 'total_amount', 'customer_phone', 'customer_email',
            'special_requests', 'created_at'
        ]



