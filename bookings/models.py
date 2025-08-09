from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid
from datetime import datetime, timedelta

User = get_user_model()

class Booking(models.Model):
    """Main booking model for appointments"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Confirmation'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Payment Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
        ('failed', 'Payment Failed'),
    ]
    
    # Basic Information
    booking_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    provider = models.ForeignKey('providers.Provider', on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey('providers.ProviderService', on_delete=models.CASCADE, related_name='bookings')
    
    # Booking Details
    booking_date = models.DateField()
    booking_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField()
    participants = models.PositiveIntegerField(default=1)
    
    # Status & Payment
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Pricing
    service_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='LKR')
    
    # Customer Information
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=15)
    customer_email = models.EmailField()
    special_requests = models.TextField(blank=True)
    
    # Booking Management
    confirmation_token = models.UUIDField(default=uuid.uuid4)
    provider_notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    cancelled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cancelled_bookings')
    
    # Reschedule Information
    original_booking = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='rescheduled_bookings')
    reschedule_count = models.PositiveIntegerField(default=0)
    
    # Notifications
    reminder_sent = models.BooleanField(default=False)
    confirmation_sent = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['provider', 'booking_date']),
            models.Index(fields=['booking_date', 'booking_time']),
            models.Index(fields=['status', 'payment_status']),
        ]
    
    def __str__(self):
        return f"Booking {self.booking_id} - {self.provider.business_name} on {self.booking_date}"
    
    @property
    def booking_datetime(self):
        """Get complete booking datetime"""
        return datetime.combine(self.booking_date, self.booking_time)
    
    @property
    def end_datetime(self):
        """Calculate booking end time"""
        return self.booking_datetime + timedelta(minutes=self.duration_minutes)
    
    @property
    def is_past(self):
        """Check if booking is in the past"""
        return self.booking_datetime < datetime.now()
    
    @property
    def can_cancel(self):
        """Check if booking can be cancelled"""
        if self.status in ['cancelled', 'completed', 'no_show']:
            return False
        # Allow cancellation up to 2 hours before booking
        return self.booking_datetime > datetime.now() + timedelta(hours=2)
    
    @property
    def can_reschedule(self):
        """Check if booking can be rescheduled"""
        if self.status in ['cancelled', 'completed', 'no_show']:
            return False
        if self.reschedule_count >= 2:  # Maximum 2 reschedules
            return False
        return self.booking_datetime > datetime.now() + timedelta(hours=24)
    
    def save(self, *args, **kwargs):
        # Calculate total amount if not set
        if not self.total_amount:
            self.total_amount = self.service_price * self.participants
        
        # Set duration from service if not set
        if not self.duration_minutes and self.service:
            self.duration_minutes = self.service.duration_minutes
            
        super().save(*args, **kwargs)


class BookingAvailability(models.Model):
    """Provider availability slots for bookings"""
    
    provider = models.ForeignKey('providers.Provider', on_delete=models.CASCADE, related_name='availability_slots')
    service = models.ForeignKey('providers.ProviderService', on_delete=models.CASCADE, null=True, blank=True)
    
    # Date and Time
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Capacity
    max_bookings = models.PositiveIntegerField(default=1)
    current_bookings = models.PositiveIntegerField(default=0)
    
    # Settings
    is_available = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    block_reason = models.CharField(max_length=200, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['provider', 'service', 'date', 'start_time']
        ordering = ['date', 'start_time']
        indexes = [
            models.Index(fields=['provider', 'date']),
            models.Index(fields=['service', 'date']),
            models.Index(fields=['is_available', 'is_blocked']),
        ]
    
    def __str__(self):
        service_name = self.service.name if self.service else "General"
        return f"{self.provider.business_name} - {service_name} on {self.date} {self.start_time}-{self.end_time}"
    
    @property
    def is_fully_booked(self):
        """Check if slot is fully booked"""
        return self.current_bookings >= self.max_bookings
    
    @property
    def available_spots(self):
        """Get number of available spots"""
        return max(0, self.max_bookings - self.current_bookings)


class BookingCancellation(models.Model):
    """Track booking cancellations and refunds"""
    
    CANCELLATION_TYPE_CHOICES = [
        ('customer', 'Customer Cancelled'),
        ('provider', 'Provider Cancelled'),
        ('system', 'System Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    REFUND_STATUS_CHOICES = [
        ('none', 'No Refund'),
        ('partial', 'Partial Refund'),
        ('full', 'Full Refund'),
        ('pending', 'Refund Pending'),
        ('processed', 'Refund Processed'),
    ]
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='cancellation_details')
    cancellation_type = models.CharField(max_length=20, choices=CANCELLATION_TYPE_CHOICES)
    
    # Refund Information
    refund_status = models.CharField(max_length=20, choices=REFUND_STATUS_CHOICES, default='none')
    refund_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    refund_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Details
    reason = models.TextField()
    cancelled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Processing
    refund_processed_at = models.DateTimeField(null=True, blank=True)
    refund_transaction_id = models.CharField(max_length=100, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Cancellation for {self.booking.booking_id} - {self.get_cancellation_type_display()}"


class BookingReminder(models.Model):
    """Booking reminders and notifications"""
    
    REMINDER_TYPE_CHOICES = [
        ('confirmation', 'Booking Confirmation'),
        ('reminder_24h', '24 Hour Reminder'),
        ('reminder_2h', '2 Hour Reminder'),
        ('follow_up', 'Post-Booking Follow Up'),
        ('cancellation', 'Cancellation Notification'),
        ('reschedule', 'Reschedule Notification'),
    ]
    
    DELIVERY_METHOD_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('push', 'Push Notification'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE_CHOICES)
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHOD_CHOICES)
    
    # Scheduling
    scheduled_for = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Content
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['scheduled_for']
        indexes = [
            models.Index(fields=['status', 'scheduled_for']),
            models.Index(fields=['booking', 'reminder_type']),
        ]
    
    def __str__(self):
        return f"{self.get_reminder_type_display()} for {self.booking.booking_id}"


class BookingPayment(models.Model):
    """Payment tracking for bookings"""
    
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Credit/Debit Card'),
        ('payhere', 'PayHere'),
        ('frimi', 'Frimi'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash Payment'),
        ('wallet', 'Digital Wallet'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    
    # Payment Details
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='LKR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Gateway Information
    gateway_transaction_id = models.CharField(max_length=200, blank=True)
    gateway_response = models.JSONField(default=dict)
    gateway_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Commission
    platform_commission = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    provider_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Processing
    processed_at = models.DateTimeField(null=True, blank=True)
    failed_reason = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['booking', 'status']),
            models.Index(fields=['gateway_transaction_id']),
            models.Index(fields=['status', 'processed_at']),
        ]
    
    def __str__(self):
        return f"Payment {self.id} for {self.booking.booking_id} - {self.amount} {self.currency}"
    
    def save(self, *args, **kwargs):
        # Calculate provider amount after commission
        if not self.provider_amount and self.amount:
            commission_rate = Decimal('0.10')  # 10% platform commission
            self.platform_commission = self.amount * commission_rate
            self.provider_amount = self.amount - self.platform_commission
        
        super().save(*args, **kwargs)