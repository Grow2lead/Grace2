from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Booking, BookingAvailability, BookingCancellation, BookingPayment
from .serializers import (
    BookingCreateSerializer, BookingListSerializer, BookingDetailSerializer,
    BookingUpdateSerializer, BookingCancellationSerializer,
    BookingPaymentSerializer, RescheduleBookingSerializer, ProviderBookingsSerializer
)
from .services import BookingService, PaymentService
from providers.models import Provider, ProviderService

class BookingPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class BookingCreateView(generics.CreateAPIView):
    """Create a new booking"""
    serializer_class = BookingCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            booking_service = BookingService()
            booking = booking_service.create_booking(
                user=request.user,
                provider=serializer.validated_data['provider'],
                service=serializer.validated_data['service'],
                booking_data=serializer.validated_data
            )
            
            response_serializer = BookingDetailSerializer(booking)
            return Response({
                'message': 'Booking created successfully',
                'booking': response_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserBookingsView(generics.ListAPIView):
    """List user's bookings"""
    serializer_class = BookingListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = BookingPagination
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related(
            'provider', 'service'
        ).order_by('-created_at')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    try:
        booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
        
        if not booking.can_cancel:
            return Response({'error': 'This booking cannot be cancelled'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        booking_service = BookingService()
        cancellation = booking_service.cancel_booking(
            booking=booking,
            cancelled_by=request.user,
            reason=request.data.get('reason', 'Customer cancellation')
        )
        
        return Response({
            'message': 'Booking cancelled successfully',
            'refund_amount': cancellation.refund_amount
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def check_availability(request):
    """Check availability for a specific provider and service"""
    try:
        provider_id = request.GET.get('provider_id')
        service_id = request.GET.get('service_id')
        date = request.GET.get('date')
        time = request.GET.get('time')
        participants = int(request.GET.get('participants', 1))
        
        if not all([provider_id, service_id, date, time]):
            return Response({'error': 'Missing required parameters'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        provider = get_object_or_404(Provider, id=provider_id)
        service = get_object_or_404(ProviderService, id=service_id)
        
        booking_service = BookingService()
        is_available, message = booking_service.check_availability(
            provider=provider,
            service=service,
            date=datetime.strptime(date, '%Y-%m-%d').date(),
            time=datetime.strptime(time, '%H:%M').time(),
            participants=participants
        )
        
        return Response({
            'available': is_available,
            'message': message
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_payment(request, booking_id):
    """Process payment for a booking"""
    try:
        booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
        
        if booking.payment_status == 'paid':
            return Response({'error': 'This booking has already been paid'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        payment_method = request.data.get('payment_method', 'payhere')
        
        payment_service = PaymentService()
        payment, success = payment_service.process_payment(
            booking=booking,
            payment_method=payment_method,
            payment_data=request.data
        )
        
        if success:
            serializer = BookingPaymentSerializer(payment)
            return Response({
                'message': 'Payment processed successfully',
                'payment': serializer.data
            })
        else:
            return Response({
                'error': 'Payment processing failed',
                'reason': payment.failed_reason
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
