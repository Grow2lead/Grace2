from django.db.models import Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta, time
from .models import Booking, BookingAvailability, BookingCancellation, BookingReminder, BookingPayment

class BookingService:
    """Service class for booking operations"""
    
    def check_availability(self, provider, service, date, time, participants=1, exclude_booking=None):
        """Check if a booking slot is available"""
        
        # Check if date is in the past
        if date < timezone.now().date():
            return False, "Cannot book appointments in the past"
        
        # Check if it's same day and time has passed
        if date == timezone.now().date():
            current_time = timezone.now().time()
            if time <= current_time:
                return False, "Cannot book appointments for past times today"
        
        # Check provider's general availability
        weekday = date.weekday()
        operating_hours = provider.operating_hours.get(self._get_weekday_name(weekday), {})
        if not operating_hours:
            return False, "Provider is not available on this day"
        
        open_time = datetime.strptime(operating_hours.get('open', '09:00'), '%H:%M').time()
        close_time = datetime.strptime(operating_hours.get('close', '17:00'), '%H:%M').time()
        
        if not (open_time <= time <= close_time):
            return False, f"Provider is not available at this time. Operating hours: {open_time} - {close_time}"
        
        # Check service-specific availability
        service_availability = provider.availability_schedule.filter(
            service=service,
            weekday=weekday,
            start_time__lte=time,
            end_time__gt=time,
            is_active=True
        ).first()
        
        if not service_availability:
            # Check general availability if no service-specific
            general_availability = provider.availability_schedule.filter(
                service__isnull=True,
                weekday=weekday,
                start_time__lte=time,
                end_time__gt=time,
                is_active=True
            ).first()
            
            if not general_availability:
                return False, "No availability found for this time slot"
            
            max_capacity = general_availability.max_bookings
        else:
            max_capacity = service_availability.max_bookings
        
        # Check existing bookings for this slot
        existing_bookings_query = Booking.objects.filter(
            provider=provider,
            service=service,
            booking_date=date,
            booking_time=time,
            status__in=['pending', 'confirmed']
        )
        
        if exclude_booking:
            existing_bookings_query = existing_bookings_query.exclude(id=exclude_booking.id)
        
        existing_participants = existing_bookings_query.aggregate(
            total=Sum('participants')
        )['total'] or 0
        
        if existing_participants + participants > max_capacity:
            available_spots = max_capacity - existing_participants
            return False, f"Not enough spots available. Only {available_spots} spots remaining"
        
        # Check minimum advance notice
        advance_hours = getattr(service, 'minimum_notice_hours', 24)
        booking_datetime = datetime.combine(date, time)
        min_booking_time = timezone.now() + timedelta(hours=advance_hours)
        
        if booking_datetime < min_booking_time:
            return False, f"Minimum {advance_hours} hours advance notice required"
        
        return True, "Available"
    
    def create_booking(self, user, provider, service, booking_data):
        """Create a new booking"""
        
        # Validate availability
        is_available, message = self.check_availability(
            provider=provider,
            service=service,
            date=booking_data['booking_date'],
            time=booking_data['booking_time'],
            participants=booking_data['participants']
        )
        
        if not is_available:
            raise ValueError(message)
        
        # Create booking
        booking = Booking.objects.create(
            user=user,
            provider=provider,
            service=service,
            service_price=service.price,
            total_amount=service.price * booking_data['participants'],
            duration_minutes=service.duration_minutes,
            **booking_data
        )
        
        # Schedule notifications
        self.schedule_booking_notifications(booking)
        
        # Update provider booking count
        provider.total_bookings += 1
        provider.save(update_fields=['total_bookings'])
        
        return booking
    
    def cancel_booking(self, booking, cancelled_by, reason, cancellation_type='customer'):
        """Cancel a booking"""
        
        if not booking.can_cancel:
            raise ValueError("This booking cannot be cancelled")
        
        # Calculate refund
        refund_amount, refund_percentage = self._calculate_refund(booking)
        
        # Create cancellation record
        cancellation = BookingCancellation.objects.create(
            booking=booking,
            cancellation_type=cancellation_type,
            reason=reason,
            cancelled_by=cancelled_by,
            refund_amount=refund_amount,
            refund_percentage=refund_percentage,
            refund_status='pending' if refund_amount > 0 else 'none'
        )
        
        # Update booking status
        booking.status = 'cancelled'
        booking.cancelled_at = timezone.now()
        booking.cancelled_by = cancelled_by
        booking.cancellation_reason = reason
        booking.save()
        
        # Schedule cancellation notification
        self.send_cancellation_notification(booking)
        
        return cancellation
    
    def reschedule_booking(self, booking, new_date, new_time, reason=''):
        """Reschedule a booking"""
        
        if not booking.can_reschedule:
            raise ValueError("This booking cannot be rescheduled")
        
        # Check new slot availability
        is_available, message = self.check_availability(
            provider=booking.provider,
            service=booking.service,
            date=new_date,
            time=new_time,
            participants=booking.participants,
            exclude_booking=booking
        )
        
        if not is_available:
            raise ValueError(message)
        
        # Create new booking for the new slot
        original_booking = booking
        new_booking = Booking.objects.create(
            user=booking.user,
            provider=booking.provider,
            service=booking.service,
            booking_date=new_date,
            booking_time=new_time,
            duration_minutes=booking.duration_minutes,
            participants=booking.participants,
            service_price=booking.service_price,
            total_amount=booking.total_amount,
            customer_name=booking.customer_name,
            customer_phone=booking.customer_phone,
            customer_email=booking.customer_email,
            special_requests=booking.special_requests,
            payment_status=booking.payment_status,
            original_booking=original_booking,
            reschedule_count=booking.reschedule_count + 1
        )
        
        # Update original booking
        original_booking.status = 'rescheduled'
        original_booking.save()
        
        # Schedule notifications for new booking
        self.schedule_booking_notifications(new_booking)
        
        return new_booking
    
    def get_available_slots(self, provider, service, date_from, date_to):
        """Get available time slots for a provider and service"""
        
        available_slots = []
        current_date = date_from
        
        while current_date <= date_to:
            weekday = current_date.weekday()
            
            # Get provider's operating hours
            operating_hours = provider.operating_hours.get(self._get_weekday_name(weekday), {})
            if not operating_hours:
                current_date += timedelta(days=1)
                continue
            
            # Get availability schedule
            schedule = provider.availability_schedule.filter(
                Q(service=service) | Q(service__isnull=True),
                weekday=weekday,
                is_active=True
            )
            
            for slot in schedule:
                # Generate time slots (e.g., every 30 minutes)
                current_time = slot.start_time
                end_time = slot.end_time
                slot_duration = timedelta(minutes=service.duration_minutes)
                
                while current_time < end_time:
                    # Check if this specific slot is available
                    is_available, _ = self.check_availability(
                        provider=provider,
                        service=service,
                        date=current_date,
                        time=current_time,
                        participants=1
                    )
                    
                    if is_available:
                        available_slots.append({
                            'date': current_date,
                            'time': current_time,
                            'available_spots': slot.max_bookings
                        })
                    
                    # Move to next slot (30-minute intervals)
                    current_time = (datetime.combine(current_date, current_time) + timedelta(minutes=30)).time()
            
            current_date += timedelta(days=1)
        
        return available_slots
    
    def schedule_booking_notifications(self, booking):
        """Schedule notifications for a booking"""
        
        booking_datetime = booking.booking_datetime
        
        # Confirmation notification (immediate)
        BookingReminder.objects.create(
            booking=booking,
            reminder_type='confirmation',
            delivery_method='email',
            scheduled_for=timezone.now(),
            subject=f'Booking Confirmation - {booking.provider.business_name}',
            message=f'Your booking for {booking.service.name} on {booking.booking_date} at {booking.booking_time} has been confirmed.'
        )
        
        # 24-hour reminder
        if booking_datetime > timezone.now() + timedelta(hours=24):
            BookingReminder.objects.create(
                booking=booking,
                reminder_type='reminder_24h',
                delivery_method='email',
                scheduled_for=booking_datetime - timedelta(hours=24),
                subject=f'Reminder: Your appointment tomorrow at {booking.provider.business_name}',
                message=f'This is a reminder for your {booking.service.name} appointment tomorrow at {booking.booking_time}.'
            )
        
        # 2-hour reminder
        if booking_datetime > timezone.now() + timedelta(hours=2):
            BookingReminder.objects.create(
                booking=booking,
                reminder_type='reminder_2h',
                delivery_method='sms',
                scheduled_for=booking_datetime - timedelta(hours=2),
                subject=f'Reminder: Appointment in 2 hours',
                message=f'Your {booking.service.name} appointment at {booking.provider.business_name} is in 2 hours.'
            )
    
    def send_cancellation_notification(self, booking):
        """Send cancellation notification"""
        
        BookingReminder.objects.create(
            booking=booking,
            reminder_type='cancellation',
            delivery_method='email',
            scheduled_for=timezone.now(),
            subject=f'Booking Cancelled - {booking.provider.business_name}',
            message=f'Your booking for {booking.service.name} on {booking.booking_date} has been cancelled.'
        )
    
    def _calculate_refund(self, booking):
        """Calculate refund amount based on cancellation policy"""
        
        booking_datetime = booking.booking_datetime
        hours_until_booking = (booking_datetime - timezone.now()).total_seconds() / 3600
        
        # Refund policy
        if hours_until_booking >= 24:
            refund_percentage = 100  # Full refund
        elif hours_until_booking >= 2:
            refund_percentage = 50   # Partial refund
        else:
            refund_percentage = 0    # No refund
        
        refund_amount = (booking.total_amount * refund_percentage) / 100
        return refund_amount, refund_percentage
    
    def _get_weekday_name(self, weekday):
        """Convert weekday number to name"""
        weekdays = {
            0: 'monday', 1: 'tuesday', 2: 'wednesday', 3: 'thursday',
            4: 'friday', 5: 'saturday', 6: 'sunday'
        }
        return weekdays.get(weekday, 'monday')

class PaymentService:
    """Service class for payment processing"""
    
    def process_payment(self, booking, payment_method, payment_data=None):
        """Process payment for a booking"""
        
        # Create payment record
        payment = BookingPayment.objects.create(
            booking=booking,
            payment_method=payment_method,
            amount=booking.total_amount,
            status='pending'
        )
        
        try:
            if payment_method == 'payhere':
                return self._process_payhere_payment(payment, payment_data)
            elif payment_method == 'frimi':
                return self._process_frimi_payment(payment, payment_data)
            elif payment_method == 'cash':
                return self._process_cash_payment(payment)
            else:
                payment.status = 'failed'
                payment.failed_reason = 'Unsupported payment method'
                payment.save()
                return payment, False
                
        except Exception as e:
            payment.status = 'failed'
            payment.failed_reason = str(e)
            payment.save()
            return payment, False
    
    def _process_payhere_payment(self, payment, payment_data):
        """Process PayHere payment"""
        
        # This would integrate with PayHere API
        # For now, simulate successful payment
        payment.status = 'completed'
        payment.gateway_transaction_id = f"PH_{timezone.now().strftime('%Y%m%d%H%M%S')}"
        payment.processed_at = timezone.now()
        payment.save()
        
        # Update booking payment status
        booking = payment.booking
        booking.payment_status = 'paid'
        booking.status = 'confirmed'
        booking.confirmed_at = timezone.now()
        booking.save()
        
        return payment, True
    
    def _process_frimi_payment(self, payment, payment_data):
        """Process Frimi payment"""
        
        # This would integrate with Frimi API
        # For now, simulate successful payment
        payment.status = 'completed'
        payment.gateway_transaction_id = f"FR_{timezone.now().strftime('%Y%m%d%H%M%S')}"
        payment.processed_at = timezone.now()
        payment.save()
        
        # Update booking payment status
        booking = payment.booking
        booking.payment_status = 'paid'
        booking.status = 'confirmed'
        booking.confirmed_at = timezone.now()
        booking.save()
        
        return payment, True
    
    def _process_cash_payment(self, payment):
        """Process cash payment (to be paid at venue)"""
        
        payment.status = 'pending'
        payment.save()
        
        # Update booking status
        booking = payment.booking
        booking.payment_status = 'pending'
        booking.status = 'confirmed'  # Confirm even with pending payment
        booking.confirmed_at = timezone.now()
        booking.save()
        
        return payment, True
