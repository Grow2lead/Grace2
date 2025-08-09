from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Booking, BookingAvailability, BookingCancellation, BookingReminder, BookingPayment

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'customer_name', 'provider', 'service', 'booking_date', 'booking_time', 'status', 'payment_status', 'total_amount')
    list_filter = ('status', 'payment_status', 'booking_date', 'provider__category', 'created_at')
    search_fields = ('booking_id', 'customer_name', 'customer_email', 'provider__business_name', 'service__name')
    readonly_fields = ('booking_id', 'confirmation_token', 'created_at', 'updated_at', 'booking_datetime_display', 'booking_actions')
    date_hierarchy = 'booking_date'
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_id', 'user', 'provider', 'service', 'booking_date', 'booking_time', 'duration_minutes', 'participants')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_phone', 'customer_email', 'special_requests')
        }),
        ('Status & Payment', {
            'fields': ('status', 'payment_status', 'service_price', 'total_amount', 'currency')
        }),
        ('Management', {
            'fields': ('provider_notes', 'cancellation_reason', 'cancelled_by', 'original_booking', 'reschedule_count')
        }),
        ('Notifications', {
            'fields': ('reminder_sent', 'confirmation_sent'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('confirmation_token', 'created_at', 'updated_at', 'confirmed_at', 'cancelled_at'),
            'classes': ('collapse',)
        }),
        ('Actions', {
            'fields': ('booking_actions',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['confirm_bookings', 'cancel_bookings', 'mark_completed', 'send_reminders']
    
    def booking_datetime_display(self, obj):
        return f"{obj.booking_date} at {obj.booking_time}"
    booking_datetime_display.short_description = "Booking Date & Time"
    
    def booking_actions(self, obj):
        actions = []
        if obj.status == 'pending':
            actions.append(f'<a href="#" onclick="confirmBooking(\'{obj.booking_id}\')">Confirm</a>')
        if obj.can_cancel:
            actions.append(f'<a href="#" onclick="cancelBooking(\'{obj.booking_id}\')">Cancel</a>')
        return format_html(' | '.join(actions)) if actions else 'No actions available'
    booking_actions.short_description = "Quick Actions"
    
    def confirm_bookings(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='confirmed',
            confirmed_at=timezone.now()
        )
        self.message_user(request, f"Successfully confirmed {updated} bookings.")
    confirm_bookings.short_description = "Confirm selected bookings"
    
    def cancel_bookings(self, request, queryset):
        updated = queryset.exclude(status__in=['cancelled', 'completed']).update(
            status='cancelled',
            cancelled_at=timezone.now(),
            cancelled_by=request.user
        )
        self.message_user(request, f"Successfully cancelled {updated} bookings.")
    cancel_bookings.short_description = "Cancel selected bookings"
    
    def mark_completed(self, request, queryset):
        updated = queryset.filter(status='confirmed').update(status='completed')
        self.message_user(request, f"Successfully marked {updated} bookings as completed.")
    mark_completed.short_description = "Mark as completed"

@admin.register(BookingAvailability)
class BookingAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('provider', 'service', 'date', 'start_time', 'end_time', 'availability_status', 'current_bookings', 'max_bookings')
    list_filter = ('is_available', 'is_blocked', 'date', 'provider__category')
    search_fields = ('provider__business_name', 'service__name')
    date_hierarchy = 'date'
    
    def availability_status(self, obj):
        if obj.is_blocked:
            return format_html('<span style="color: red;">Blocked</span>')
        elif not obj.is_available:
            return format_html('<span style="color: orange;">Unavailable</span>')
        elif obj.is_fully_booked:
            return format_html('<span style="color: blue;">Fully Booked</span>')
        else:
            return format_html('<span style="color: green;">Available</span>')
    availability_status.short_description = "Status"

@admin.register(BookingCancellation)
class BookingCancellationAdmin(admin.ModelAdmin):
    list_display = ('booking', 'cancellation_type', 'refund_status', 'refund_amount', 'cancelled_by', 'created_at')
    list_filter = ('cancellation_type', 'refund_status', 'created_at')
    search_fields = ('booking__booking_id', 'booking__customer_name', 'reason')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Cancellation Details', {
            'fields': ('booking', 'cancellation_type', 'reason', 'cancelled_by')
        }),
        ('Refund Information', {
            'fields': ('refund_status', 'refund_amount', 'refund_percentage', 'refund_processed_at', 'refund_transaction_id')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(BookingReminder)
class BookingReminderAdmin(admin.ModelAdmin):
    list_display = ('booking', 'reminder_type', 'delivery_method', 'status', 'scheduled_for', 'sent_at')
    list_filter = ('reminder_type', 'delivery_method', 'status', 'scheduled_for')
    search_fields = ('booking__booking_id', 'booking__customer_name', 'subject')
    date_hierarchy = 'scheduled_for'
    
    fieldsets = (
        ('Reminder Details', {
            'fields': ('booking', 'reminder_type', 'delivery_method', 'scheduled_for')
        }),
        ('Content', {
            'fields': ('subject', 'message')
        }),
        ('Status', {
            'fields': ('status', 'sent_at', 'error_message')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(BookingPayment)
class BookingPaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'payment_method', 'amount', 'status', 'gateway_transaction_id', 'processed_at')
    list_filter = ('payment_method', 'status', 'processed_at', 'created_at')
    search_fields = ('booking__booking_id', 'gateway_transaction_id', 'booking__customer_name')
    readonly_fields = ('created_at', 'updated_at', 'platform_commission', 'provider_amount')
    
    fieldsets = (
        ('Payment Details', {
            'fields': ('booking', 'payment_method', 'amount', 'currency', 'status')
        }),
        ('Gateway Information', {
            'fields': ('gateway_transaction_id', 'gateway_response', 'gateway_fee')
        }),
        ('Commission & Fees', {
            'fields': ('platform_commission', 'provider_amount'),
            'classes': ('collapse',)
        }),
        ('Processing', {
            'fields': ('processed_at', 'failed_reason')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )