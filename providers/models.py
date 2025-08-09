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


class FitnessCenter(models.Model):
    """Extended model for fitness centers with specialized features"""
    
    FITNESS_TYPE_CHOICES = [
        ('gym', 'Gym & Fitness Center'),
        ('zumba', 'Zumba & Dance Studio'),
        ('crossfit', 'CrossFit Box'),
        ('yoga', 'Yoga Studio'),
        ('martial_arts', 'Martial Arts School'),
        ('personal_training', 'Personal Training Studio'),
        ('multi_purpose', 'Multi-Purpose Fitness Center'),
    ]
    
    MEMBERSHIP_TYPE_CHOICES = [
        ('monthly', 'Monthly Membership'),
        ('quarterly', 'Quarterly Membership'),
        ('annual', 'Annual Membership'),
        ('daily', 'Daily Pass'),
        ('session', 'Per Session'),
    ]
    
    provider = models.OneToOneField(Provider, on_delete=models.CASCADE, related_name='fitness_details')
    fitness_type = models.CharField(max_length=20, choices=FITNESS_TYPE_CHOICES)
    
    # Facility Details
    total_area_sqft = models.PositiveIntegerField(null=True, blank=True, help_text="Total area in square feet")
    max_capacity = models.PositiveIntegerField(default=50, help_text="Maximum number of people at once")
    parking_spaces = models.PositiveIntegerField(default=0)
    
    # Equipment & Facilities
    available_equipment = models.JSONField(default=list, help_text="List of available equipment")
    has_air_conditioning = models.BooleanField(default=True)
    has_shower_facilities = models.BooleanField(default=True)
    has_locker_rooms = models.BooleanField(default=True)
    has_changing_rooms = models.BooleanField(default=True)
    has_parking = models.BooleanField(default=True)
    has_water_station = models.BooleanField(default=True)
    
    # Membership & Pricing
    membership_types = models.JSONField(default=list, help_text="Available membership types")
    trial_class_available = models.BooleanField(default=True)
    trial_class_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Class Schedule
    group_classes_available = models.BooleanField(default=True)
    personal_training_available = models.BooleanField(default=True)
    
    # Special Features
    nutritionist_available = models.BooleanField(default=False)
    physiotherapist_available = models.BooleanField(default=False)
    massage_therapy_available = models.BooleanField(default=False)
    
    # Age Restrictions
    min_age = models.PositiveIntegerField(default=16)
    kids_programs_available = models.BooleanField(default=False)
    senior_programs_available = models.BooleanField(default=False)
    
    # Safety & Hygiene
    covid_safety_measures = models.JSONField(default=list, help_text="COVID-19 safety measures")
    first_aid_certified_staff = models.BooleanField(default=False)
    
    # Business Hours Extensions
    early_morning_access = models.BooleanField(default=False, help_text="Access before 6 AM")
    late_night_access = models.BooleanField(default=False, help_text="Access after 10 PM")
    twenty_four_seven = models.BooleanField(default=False, help_text="24/7 access")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Fitness Center"
        verbose_name_plural = "Fitness Centers"
        
    def __str__(self):
        return f"{self.provider.business_name} - {self.get_fitness_type_display()}"
    
    @property
    def is_gym(self):
        return self.fitness_type == 'gym'
    
    @property
    def is_dance_studio(self):
        return self.fitness_type in ['zumba', 'dance']
    
    @property
    def available_equipment_list(self):
        """Get equipment as formatted list"""
        return self.available_equipment if isinstance(self.available_equipment, list) else []


class FitnessInstructor(models.Model):
    """Model for fitness instructors/trainers"""
    
    SPECIALIZATION_CHOICES = [
        ('personal_training', 'Personal Training'),
        ('group_fitness', 'Group Fitness'),
        ('zumba', 'Zumba'),
        ('yoga', 'Yoga'),
        ('pilates', 'Pilates'),
        ('crossfit', 'CrossFit'),
        ('boxing', 'Boxing'),
        ('martial_arts', 'Martial Arts'),
        ('dance', 'Dance'),
        ('aerobics', 'Aerobics'),
        ('strength_training', 'Strength Training'),
        ('cardio', 'Cardio Training'),
        ('nutrition', 'Nutrition Counseling'),
        ('rehabilitation', 'Rehabilitation'),
    ]
    
    fitness_center = models.ForeignKey(FitnessCenter, on_delete=models.CASCADE, related_name='instructors')
    name = models.CharField(max_length=200)
    name_si = models.CharField(max_length=200, blank=True)
    name_ta = models.CharField(max_length=200, blank=True)
    
    specializations = models.JSONField(default=list, help_text="List of specializations")
    bio = models.TextField(blank=True)
    
    # Qualifications
    certifications = models.JSONField(default=list, help_text="List of certifications")
    years_experience = models.PositiveIntegerField(default=0)
    
    # Availability
    available_days = models.JSONField(default=list, help_text="Days of the week available")
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Contact
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    
    # Ratings
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0,
                                        validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_reviews = models.PositiveIntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-average_rating', 'name']
        
    def __str__(self):
        return f"{self.name} - {self.fitness_center.provider.business_name}"


class FitnessClassSchedule(models.Model):
    """Model for fitness class schedules"""
    
    WEEKDAY_CHOICES = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ]
    
    DIFFICULTY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('all_levels', 'All Levels'),
    ]
    
    fitness_center = models.ForeignKey(FitnessCenter, on_delete=models.CASCADE, related_name='class_schedules')
    instructor = models.ForeignKey(FitnessInstructor, on_delete=models.CASCADE, related_name='class_schedules')
    service = models.ForeignKey(ProviderService, on_delete=models.CASCADE, related_name='class_schedules')
    
    # Class Details
    class_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='all_levels')
    
    # Schedule
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Capacity
    max_participants = models.PositiveIntegerField(default=20)
    
    # Pricing
    drop_in_price = models.DecimalField(max_digits=8, decimal_places=2)
    package_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    package_sessions = models.PositiveIntegerField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['fitness_center', 'weekday', 'start_time']
        ordering = ['weekday', 'start_time']
        
    def __str__(self):
        weekday_name = dict(self.WEEKDAY_CHOICES)[self.weekday]
        return f"{self.class_name} - {weekday_name} {self.start_time}"


class FitnessMembership(models.Model):
    """Model for fitness center memberships"""
    
    MEMBERSHIP_STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fitness_memberships')
    fitness_center = models.ForeignKey(FitnessCenter, on_delete=models.CASCADE, related_name='memberships')
    
    # Membership Details
    membership_type = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=MEMBERSHIP_STATUS_CHOICES, default='active')
    
    # Payment
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2)
    payment_method = models.CharField(max_length=50, blank=True)
    
    # Usage
    total_visits = models.PositiveIntegerField(default=0)
    last_visit = models.DateField(null=True, blank=True)
    
    # Settings
    auto_renewal = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'fitness_center']
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.fitness_center.provider.business_name}"
    
    @property
    def is_active(self):
        from django.utils import timezone
        return self.status == 'active' and self.end_date >= timezone.now().date()
    
    @property
    def days_remaining(self):
        from django.utils import timezone
        if self.end_date >= timezone.now().date():
            return (self.end_date - timezone.now().date()).days
        return 0