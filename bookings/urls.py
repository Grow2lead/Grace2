from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    # Customer booking management
    path('', views.UserBookingsView.as_view(), name='user-bookings'),
    path('create/', views.BookingCreateView.as_view(), name='create-booking'),
    path('<uuid:booking_id>/cancel/', views.cancel_booking, name='cancel-booking'),
    path('<uuid:booking_id>/payment/', views.process_payment, name='process-payment'),
    
    # Availability checking
    path('availability/check/', views.check_availability, name='check-availability'),
    
    # Provider endpoints (will be added later for full implementation)
    # path('provider/', views.ProviderBookingsView.as_view(), name='provider-bookings'),
    # path('<uuid:booking_id>/confirm/', views.confirm_booking, name='confirm-booking'),
]



