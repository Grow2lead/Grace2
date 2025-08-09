from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
import uuid

User = get_user_model()

class Provider(models.Model):
    """Main provider model for wellness marketplace"""
    
    CATEGORY_CHOICES = [
        ('millet_food', 'Millet Food Shops'),
        ('gym', 'Gyms & Fitness Centers'),
        ('zumba', 'Zumba & Dance Studios'),
        ('nutritionist', 'Nutritionists & Dietitians'),
        ('dietitian', 'Clinical Dietitians'),
        ('meal_delivery', 'Meal Delivery Services'),
        ('healthy_food', 'Healthy Food Stores'),
        ('yoga', 'Yoga Studios'),
        ('personal_trainer', 'Personal Trainers'),
        ('ayurveda', 'Ayurvedic Centers'),
        ('mental_health', 'Mental Health Counselors'),
        ('spa', 'Spas & Wellness Centers'),
        ('physiotherapy', 'Physiotherapy Centers'),
        ('meditation', 'Meditation Centers'),
        ('martial_arts', 'Martial Arts Schools'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
        ('inactive', 'Inactive'),
    ]
    
    DISTRICT_CHOICES = [
        ('colombo', 'Colombo'),
        ('gampaha', 'Gampaha'),
        ('kalutara', 'Kalutara'),
        ('kandy', 'Kandy'),
        ('matale', 'Matale'),
        ('nuwara_eliya', 'Nuwara Eliya'),
        ('galle', 'Galle'),
        ('matara', 'Matara'),
        ('hambantota', 'Hambantota'),
        ('jaffna', 'Jaffna'),
        ('kurunegala', 'Kurunegala'),
        ('anuradhapura', 'Anuradhapura'),
        ('badulla', 'Badulla'),
        ('ratnapura', 'Ratnapura'),
        ('ampara', 'Ampara'),
        ('batticaloa', 'Batticaloa'),
        ('trincomalee', 'Trincomalee'),
    ]
    
    # Basic Information
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider_profile')
    business_name = models.CharField(max_length=200)
    business_name_si = models.CharField(max_length=200, blank=True, help_text="Business name in Sinhala")
    business_name_ta = models.CharField(max_length=200, blank=True, help_text="Business name in Tamil")
    
    # Classification
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    subcategory = models.CharField(max_length=100, blank=True, help_text="Specific type within category")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Contact Information
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    whatsapp = models.CharField(max_length=15, blank=True)
    website = models.URLField(blank=True)
    
    # Location
    address = models.TextField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=50, choices=DISTRICT_CHOICES)
    postal_code = models.CharField(max_length=10, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Business Details
    description = models.TextField()
    description_si = models.TextField(blank=True, help_text="Description in Sinhala")
    description_ta = models.TextField(blank=True, help_text="Description in Tamil")
    
    # Operating Information
    operating_hours = models.JSONField(default=dict, help_text="Weekly operating hours")
    amenities = models.JSONField(default=list, help_text="Available amenities")
    pricing_info = models.TextField(blank=True, help_text="General pricing information")
    
    # Verification & Trust
    is_verified = models.BooleanField(default=False)
    verification_documents = models.FileField(upload_to='provider_verifications/', blank=True)
    
    # Performance Metrics
    total_bookings = models.PositiveIntegerField(default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0,
                                        validators=[MinValueValidator(0), MaxValueValidator(5)])
    
    # Business Settings
    accepts_online_bookings = models.BooleanField(default=True)
    cancellation_policy = models.TextField(blank=True)
    
    # SEO & Marketing
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'district']),
            models.Index(fields=['status', 'is_verified']),
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def __str__(self):
        return self.business_name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.business_name)
            slug = base_slug
            counter = 1
            while Provider.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def get_localized_name(self, language='en'):
        """Get business name in specified language"""
        if language == 'si' and self.business_name_si:
            return self.business_name_si
        elif language == 'ta' and self.business_name_ta:
            return self.business_name_ta
        return self.business_name


class ProviderService(models.Model):
    """Services offered by providers"""
    
    SERVICE_TYPE_CHOICES = [
        ('consultation', 'Consultation'),
        ('session', 'Training Session'),
        ('class', 'Group Class'),
        ('workshop', 'Workshop'),
        ('treatment', 'Treatment'),
        ('package', 'Package Deal'),
    ]
    
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200)
    name_si = models.CharField(max_length=200, blank=True)
    name_ta = models.CharField(max_length=200, blank=True)
    
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES)
    description = models.TextField()
    
    # Pricing
    price = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='LKR')
    duration_minutes = models.PositiveIntegerField()
    max_participants = models.PositiveIntegerField(default=1)
    
    # Availability
    is_bookable = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return f"{self.provider.business_name} - {self.name}"


class ProviderMedia(models.Model):
    """Media files for providers"""
    
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='media')
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='provider_images/', blank=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['sort_order', '-uploaded_at']
    
    def __str__(self):
        return f"{self.provider.business_name} - {self.title or 'Media'}"