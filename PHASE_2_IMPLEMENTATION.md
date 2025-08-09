# Phase 2 Implementation Guide: Provider Marketplace

## Overview
**Timeline**: Q2 2025 (3 months)  
**Budget**: $120,000  
**Goal**: Launch comprehensive provider directory and basic booking system

## Week-by-Week Implementation Plan

### Week 1-3: Provider Management System

#### Provider Profile Models
```python
# Create new app: providers
python manage.py startapp providers

# providers/models.py
class Provider(models.Model):
    CATEGORY_CHOICES = [
        ('millet_food', 'Millet Food Shops'),
        ('gym', 'Gyms & Fitness Centers'),
        ('zumba', 'Zumba & Dance Studios'),
        ('nutritionist', 'Nutritionists & Dietitians'),
        ('yoga', 'Yoga Studios'),
        ('personal_trainer', 'Personal Trainers'),
        ('ayurveda', 'Ayurvedic Centers'),
        ('mental_health', 'Mental Health Counselors'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Contact Information
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    website = models.URLField(blank=True)
    
    # Location
    address = models.TextField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    
    # Business Details
    description = models.TextField()
    operating_hours = models.JSONField(default=dict)
    amenities = models.JSONField(default=list)
    pricing_info = models.TextField(blank=True)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verification_documents = models.FileField(upload_to='verifications/', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ProviderService(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200)
    description = models.TextField()
    duration_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_bookable = models.BooleanField(default=True)
    max_participants = models.IntegerField(default=1)

class ProviderMedia(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='media')
    image = models.ImageField(upload_to='provider_images/')
    caption = models.CharField(max_length=500, blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
```

#### Provider Registration API
```python
# providers/serializers.py
class ProviderRegistrationSerializer(serializers.ModelSerializer):
    services = serializers.JSONField(write_only=True)
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    
    class Meta:
        model = Provider
        fields = ['business_name', 'category', 'email', 'phone', 'website',
                 'address', 'city', 'district', 'description', 'operating_hours',
                 'amenities', 'pricing_info', 'services', 'images']
    
    def create(self, validated_data):
        services_data = validated_data.pop('services', [])
        images_data = validated_data.pop('images', [])
        
        provider = Provider.objects.create(**validated_data)
        
        # Create services
        for service_data in services_data:
            ProviderService.objects.create(provider=provider, **service_data)
        
        # Upload images
        for i, image in enumerate(images_data):
            ProviderMedia.objects.create(
                provider=provider, 
                image=image, 
                order=i,
                is_featured=(i == 0)
            )
        
        return provider

# providers/views.py
class ProviderRegistrationView(generics.CreateAPIView):
    serializer_class = ProviderRegistrationSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
```

### Week 4-6: Search & Discovery System

#### Advanced Search Implementation
```python
# Create new app: search
python manage.py startapp search

# search/models.py
class SearchIndex(models.Model):
    provider = models.OneToOneField(Provider, on_delete=models.CASCADE)
    search_vector = models.TextField()  # For full-text search
    category_tags = models.JSONField(default=list)
    location_tags = models.JSONField(default=list)
    amenity_tags = models.JSONField(default=list)
    
    class Meta:
        indexes = [
            models.Index(fields=['search_vector']),
        ]

# search/services.py
class ProviderSearchService:
    def __init__(self):
        self.elasticsearch_client = None  # Initialize if using Elasticsearch
    
    def search_providers(self, query_params):
        """
        Advanced search with filters
        """
        queryset = Provider.objects.filter(status='approved')
        
        # Text search
        if query_params.get('q'):
            queryset = queryset.filter(
                Q(business_name__icontains=query_params['q']) |
                Q(description__icontains=query_params['q']) |
                Q(services__name__icontains=query_params['q'])
            ).distinct()
        
        # Category filter
        if query_params.get('category'):
            queryset = queryset.filter(category=query_params['category'])
        
        # Location filter
        if query_params.get('city'):
            queryset = queryset.filter(city__iexact=query_params['city'])
        
        # Distance-based search
        if query_params.get('lat') and query_params.get('lng'):
            lat = float(query_params['lat'])
            lng = float(query_params['lng'])
            radius = float(query_params.get('radius', 10))  # km
            
            queryset = self._filter_by_distance(queryset, lat, lng, radius)
        
        # Price range filter
        if query_params.get('min_price') or query_params.get('max_price'):
            queryset = self._filter_by_price(queryset, query_params)
        
        return queryset
    
    def _filter_by_distance(self, queryset, lat, lng, radius):
        # Haversine formula for distance calculation
        from django.db.models import Case, When, Value
        from math import radians, cos, sin, asin, sqrt
        
        # This is a simplified version - in production, use PostGIS
        return queryset.extra(
            select={
                'distance': """
                    6371 * acos(
                        cos(radians(%s)) * cos(radians(latitude)) * 
                        cos(radians(longitude) - radians(%s)) + 
                        sin(radians(%s)) * sin(radians(latitude))
                    )
                """
            },
            select_params=[lat, lng, lat],
            where=["6371 * acos(cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - radians(%s)) + sin(radians(%s)) * sin(radians(latitude))) <= %s"],
            params=[lat, lng, lat, radius],
            order_by=['distance']
        )

# search/views.py
class ProviderSearchView(generics.ListAPIView):
    serializer_class = ProviderSearchSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        search_service = ProviderSearchService()
        return search_service.search_providers(self.request.query_params)
```

#### Map Integration
```python
# providers/views.py
class ProviderMapView(APIView):
    def get(self, request):
        providers = Provider.objects.filter(
            status='approved',
            latitude__isnull=False,
            longitude__isnull=False
        )
        
        # Apply same filters as search
        search_service = ProviderSearchService()
        providers = search_service.search_providers(request.query_params)
        
        map_data = []
        for provider in providers:
            map_data.append({
                'id': provider.id,
                'name': provider.business_name,
                'category': provider.category,
                'lat': float(provider.latitude),
                'lng': float(provider.longitude),
                'rating': provider.average_rating if hasattr(provider, 'average_rating') else 0,
                'image': provider.featured_image_url if hasattr(provider, 'featured_image_url') else None
            })
        
        return Response({'providers': map_data})
```

### Week 7-9: Booking & Reservation System

#### Booking Models
```python
# Create new app: bookings
python manage.py startapp bookings

# bookings/models.py
class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Confirmation'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    service = models.ForeignKey(ProviderService, on_delete=models.CASCADE)
    
    booking_date = models.DateField()
    booking_time = models.TimeField()
    duration_minutes = models.IntegerField()
    
    participants = models.IntegerField(default=1)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Customer details
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=15)
    customer_email = models.EmailField()
    special_requests = models.TextField(blank=True)
    
    # Booking management
    confirmation_token = models.UUIDField(default=uuid.uuid4)
    cancellation_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ProviderAvailability(models.Model):
    WEEKDAY_CHOICES = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ]
    
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    service = models.ForeignKey(ProviderService, on_delete=models.CASCADE)
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_bookings = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

class BookingNotification(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_successful = models.BooleanField(default=True)
```

#### Booking Service Logic
```python
# bookings/services.py
class BookingService:
    def check_availability(self, provider, service, date, time, participants=1):
        """Check if booking slot is available"""
        weekday = date.weekday()
        
        # Check if provider offers service on this day/time
        availability = ProviderAvailability.objects.filter(
            provider=provider,
            service=service,
            weekday=weekday,
            start_time__lte=time,
            end_time__gt=time,
            is_active=True
        ).first()
        
        if not availability:
            return False, "Provider not available at this time"
        
        # Check existing bookings
        existing_bookings = Booking.objects.filter(
            provider=provider,
            service=service,
            booking_date=date,
            booking_time=time,
            status__in=['pending', 'confirmed']
        ).aggregate(
            total_participants=models.Sum('participants')
        )['total_participants'] or 0
        
        if existing_bookings + participants > availability.max_bookings:
            return False, "Not enough slots available"
        
        return True, "Available"
    
    def create_booking(self, user, provider, service, booking_data):
        """Create a new booking"""
        # Validate availability
        is_available, message = self.check_availability(
            provider, service, 
            booking_data['booking_date'],
            booking_data['booking_time'],
            booking_data['participants']
        )
        
        if not is_available:
            raise ValidationError(message)
        
        # Calculate total amount
        total_amount = service.price * booking_data['participants']
        
        # Create booking
        booking = Booking.objects.create(
            user=user,
            provider=provider,
            service=service,
            total_amount=total_amount,
            **booking_data
        )
        
        # Send notifications
        self.send_booking_notifications(booking)
        
        return booking
    
    def send_booking_notifications(self, booking):
        """Send booking confirmation notifications"""
        # Email to customer
        self.send_customer_confirmation(booking)
        
        # Notification to provider
        self.send_provider_notification(booking)
        
        # SMS reminders (if enabled)
        self.schedule_reminder_notifications(booking)
```

### Week 10-12: Payment Integration & Quality Assurance

#### Payment Gateway Integration
```python
# Create new app: payments
python manage.py startapp payments

# payments/models.py
class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='LKR')
    payment_method = models.CharField(max_length=50)
    
    # Gateway details
    gateway_transaction_id = models.CharField(max_length=200, blank=True)
    gateway_response = models.JSONField(default=dict)
    
    status = models.CharField(max_length=20, default='pending')
    processed_at = models.DateTimeField(null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

# payments/services.py
class PaymentService:
    def __init__(self, gateway='payhere'):
        self.gateway = gateway
    
    def process_payment(self, booking, payment_data):
        """Process payment through selected gateway"""
        if self.gateway == 'payhere':
            return self._process_payhere_payment(booking, payment_data)
        elif self.gateway == 'frimi':
            return self._process_frimi_payment(booking, payment_data)
    
    def _process_payhere_payment(self, booking, payment_data):
        # PayHere integration
        import requests
        
        payload = {
            'merchant_id': settings.PAYHERE_MERCHANT_ID,
            'order_id': f"BOOKING_{booking.id}",
            'amount': str(booking.total_amount),
            'currency': 'LKR',
            'return_url': f"{settings.FRONTEND_URL}/booking/success",
            'cancel_url': f"{settings.FRONTEND_URL}/booking/cancel",
            'notify_url': f"{settings.BACKEND_URL}/payments/payhere/notify/",
        }
        
        # Create payment record
        payment = Payment.objects.create(
            booking=booking,
            amount=booking.total_amount,
            payment_method='payhere',
            status='pending'
        )
        
        return payment, payload
```

#### Review & Rating System
```python
# reviews/models.py
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True)
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    
    # Review media
    images = models.JSONField(default=list)
    
    # Moderation
    is_verified = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'booking']

# Update Provider model with rating aggregation
class Provider(models.Model):
    # ... existing fields ...
    
    @property
    def average_rating(self):
        reviews = Review.objects.filter(provider=self, is_verified=True)
        if reviews.exists():
            return reviews.aggregate(Avg('rating'))['rating__avg']
        return 0
    
    @property
    def total_reviews(self):
        return Review.objects.filter(provider=self, is_verified=True).count()
```

## API Endpoints Summary

### Provider Management
```python
# providers/urls.py
urlpatterns = [
    path('register/', ProviderRegistrationView.as_view(), name='provider-register'),
    path('profile/', ProviderProfileView.as_view(), name='provider-profile'),
    path('dashboard/', ProviderDashboardView.as_view(), name='provider-dashboard'),
    path('<int:pk>/', ProviderDetailView.as_view(), name='provider-detail'),
    path('categories/', ProviderCategoriesView.as_view(), name='provider-categories'),
]

# search/urls.py
urlpatterns = [
    path('providers/', ProviderSearchView.as_view(), name='provider-search'),
    path('providers/map/', ProviderMapView.as_view(), name='provider-map'),
    path('suggestions/', SearchSuggestionsView.as_view(), name='search-suggestions'),
]

# bookings/urls.py
urlpatterns = [
    path('create/', BookingCreateView.as_view(), name='booking-create'),
    path('availability/', CheckAvailabilityView.as_view(), name='check-availability'),
    path('<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),
    path('<int:pk>/cancel/', BookingCancelView.as_view(), name='booking-cancel'),
    path('user/', UserBookingsView.as_view(), name='user-bookings'),
]
```

## Frontend Components (React)

### Provider Search Interface
```javascript
// components/Search/ProviderSearch.jsx
import React, { useState, useEffect } from 'react';
import { GoogleMap, Marker } from '@react-google-maps/api';

const ProviderSearch = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [filters, setFilters] = useState({
        category: '',
        city: '',
        radius: 10,
        priceRange: [0, 10000]
    });
    const [providers, setProviders] = useState([]);
    const [mapView, setMapView] = useState(false);
    
    // Search implementation
    // Map integration
    // Filter UI
    
    return (
        <div className="provider-search">
            {/* Search bar, filters, results, map */}
        </div>
    );
};
```

### Booking Flow
```javascript
// components/Booking/BookingFlow.jsx
const BookingFlow = ({ providerId, serviceId }) => {
    const [step, setStep] = useState(1);
    const [bookingData, setBookingData] = useState({});
    
    const steps = [
        'Select Date & Time',
        'Customer Details',
        'Payment',
        'Confirmation'
    ];
    
    // Multi-step booking process
    // Availability checking
    // Payment integration
    
    return (
        <div className="booking-flow">
            {/* Step indicator, forms, payment */}
        </div>
    );
};
```

## Testing Strategy

### Unit Tests
```python
# tests/test_providers.py
class ProviderTestCase(TestCase):
    def test_provider_registration(self):
        # Test provider registration flow
        pass
    
    def test_provider_search(self):
        # Test search functionality
        pass

# tests/test_bookings.py
class BookingTestCase(TestCase):
    def test_availability_check(self):
        # Test availability logic
        pass
    
    def test_booking_creation(self):
        # Test booking process
        pass
    
    def test_payment_processing(self):
        # Test payment integration
        pass
```

### Integration Tests
```python
# tests/test_integration.py
class MarketplaceIntegrationTest(TestCase):
    def test_end_to_end_booking_flow(self):
        # Test complete user journey from search to booking
        pass
    
    def test_provider_dashboard_workflow(self):
        # Test provider management features
        pass
```

## Success Metrics for Phase 2

### Provider Adoption
- ✅ 500+ verified providers registered
- ✅ 80% provider approval rate within 48 hours
- ✅ Average provider profile completion rate >90%

### Booking System Performance
- ✅ 1000+ successful bookings completed
- ✅ Payment success rate >98%
- ✅ Booking confirmation time <30 seconds
- ✅ Average provider response time <2 hours

### User Experience
- ✅ Search relevance score >80%
- ✅ Mobile booking completion rate >70%
- ✅ User satisfaction score >4.2/5
- ✅ Provider satisfaction score >4.0/5

### Technical Performance
- ✅ API response time <500ms
- ✅ Search results loading <2 seconds
- ✅ Map rendering <3 seconds
- ✅ 99.5% system uptime

## Revenue Targets for Phase 2

### Month 1
- 50 provider registrations
- 100 bookings
- $1,000 commission revenue

### Month 2
- 200 provider registrations
- 500 bookings
- $5,000 commission revenue

### Month 3
- 500 provider registrations
- 1,000 bookings
- $15,000 commission revenue
- 50 premium provider subscriptions

## Deployment Plan

### Staging Environment
- Complete feature testing
- Load testing with simulated users
- Payment gateway testing (sandbox)
- Provider onboarding testing

### Production Deployment
- Blue-green deployment strategy
- Database migrations during low-traffic hours
- Monitoring and alerting setup
- Rollback plan preparation

This implementation guide provides the comprehensive roadmap for transforming your platform into a full marketplace during Phase 2, with detailed technical specifications and clear success metrics.
