from rest_framework import generics, status, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count, Avg
from decimal import Decimal
import math

from .models import (
    Provider, FitnessCenter, FitnessInstructor, 
    FitnessClassSchedule, FitnessMembership
)
from .fitness_serializers import (
    FitnessCenterListSerializer, FitnessCenterDetailSerializer,
    FitnessInstructorSerializer, FitnessClassScheduleSerializer,
    FitnessMembershipSerializer, FitnessSearchSerializer
)

class FitnessCenterPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class FitnessCenterListView(generics.ListAPIView):
    """List all fitness centers with filtering and search"""
    serializer_class = FitnessCenterListSerializer
    pagination_class = FitnessCenterPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['provider__business_name', 'provider__city', 'provider__district']
    ordering_fields = ['provider__average_rating', 'provider__total_reviews', 'trial_class_price']
    ordering = ['-provider__average_rating']

    def get_queryset(self):
        queryset = FitnessCenter.objects.select_related('provider').filter(
            provider__status='approved'
        )
        
        # Filter by fitness type
        fitness_type = self.request.query_params.get('fitness_type')
        if fitness_type:
            queryset = queryset.filter(fitness_type=fitness_type)
        
        # Filter by district
        district = self.request.query_params.get('district')
        if district:
            queryset = queryset.filter(provider__district=district)
        
        # Filter by features
        if self.request.query_params.get('has_parking') == 'true':
            queryset = queryset.filter(has_parking=True)
        
        if self.request.query_params.get('has_shower_facilities') == 'true':
            queryset = queryset.filter(has_shower_facilities=True)
        
        if self.request.query_params.get('personal_training_available') == 'true':
            queryset = queryset.filter(personal_training_available=True)
        
        if self.request.query_params.get('group_classes_available') == 'true':
            queryset = queryset.filter(group_classes_available=True)
        
        if self.request.query_params.get('trial_class_available') == 'true':
            queryset = queryset.filter(trial_class_available=True)
        
        # Filter by minimum rating
        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            try:
                queryset = queryset.filter(provider__average_rating__gte=Decimal(min_rating))
            except:
                pass
        
        # Filter by maximum trial price
        max_price = self.request.query_params.get('max_price')
        if max_price:
            try:
                queryset = queryset.filter(trial_class_price__lte=Decimal(max_price))
            except:
                pass
        
        # Location-based filtering
        lat = self.request.query_params.get('latitude')
        lng = self.request.query_params.get('longitude')
        radius = self.request.query_params.get('radius_km', 10)
        
        if lat and lng:
            try:
                radius_km = float(radius)
                queryset = queryset.filter(
                    provider__latitude__isnull=False,
                    provider__longitude__isnull=False
                )
                # This is a simplified distance filter - in production, use PostGIS
                # For now, we'll filter by rough bounding box
                lat_delta = radius_km / 111.0  # Rough conversion
                lng_delta = radius_km / (111.0 * math.cos(math.radians(float(lat))))
                
                queryset = queryset.filter(
                    provider__latitude__range=[float(lat) - lat_delta, float(lat) + lat_delta],
                    provider__longitude__range=[float(lng) - lng_delta, float(lng) + lng_delta]
                )
            except:
                pass
        
        return queryset

class FitnessCenterDetailView(generics.RetrieveAPIView):
    """Get detailed information about a fitness center"""
    serializer_class = FitnessCenterDetailSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        return FitnessCenter.objects.select_related('provider').prefetch_related(
            'instructors', 'class_schedules', 'class_schedules__instructor'
        ).filter(provider__status='approved')

class FitnessInstructorListView(generics.ListAPIView):
    """List instructors for a specific fitness center"""
    serializer_class = FitnessInstructorSerializer
    
    def get_queryset(self):
        fitness_center_id = self.kwargs.get('fitness_center_id')
        return FitnessInstructor.objects.filter(
            fitness_center_id=fitness_center_id,
            is_active=True
        ).order_by('-average_rating')

class FitnessClassScheduleListView(generics.ListAPIView):
    """List class schedules for a specific fitness center"""
    serializer_class = FitnessClassScheduleSerializer
    
    def get_queryset(self):
        fitness_center_id = self.kwargs.get('fitness_center_id')
        queryset = FitnessClassSchedule.objects.select_related(
            'instructor', 'service'
        ).filter(
            fitness_center_id=fitness_center_id,
            is_active=True
        ).order_by('weekday', 'start_time')
        
        # Filter by weekday if specified
        weekday = self.request.query_params.get('weekday')
        if weekday:
            try:
                queryset = queryset.filter(weekday=int(weekday))
            except:
                pass
        
        return queryset

class UserFitnessMembershipsView(generics.ListCreateAPIView):
    """List and create user fitness memberships"""
    serializer_class = FitnessMembershipSerializer
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return FitnessMembership.objects.select_related(
                'fitness_center', 'fitness_center__provider'
            ).filter(user=self.request.user).order_by('-created_at')
        return FitnessMembership.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@api_view(['GET'])
def fitness_center_stats(request):
    """Get statistics about fitness centers"""
    stats = {
        'total_centers': FitnessCenter.objects.filter(provider__status='approved').count(),
        'gyms': FitnessCenter.objects.filter(fitness_type='gym', provider__status='approved').count(),
        'zumba_studios': FitnessCenter.objects.filter(fitness_type='zumba', provider__status='approved').count(),
        'districts': FitnessCenter.objects.filter(
            provider__status='approved'
        ).values('provider__district').annotate(
            count=Count('id')
        ).order_by('-count'),
        'avg_rating': FitnessCenter.objects.filter(
            provider__status='approved'
        ).aggregate(
            avg_rating=Avg('provider__average_rating')
        )['avg_rating'] or 0,
        'total_instructors': FitnessInstructor.objects.filter(is_active=True).count(),
    }
    
    return Response(stats)

@api_view(['GET'])
def fitness_center_types(request):
    """Get available fitness center types with counts"""
    types = FitnessCenter.objects.filter(
        provider__status='approved'
    ).values('fitness_type').annotate(
        count=Count('id'),
        avg_rating=Avg('provider__average_rating')
    ).order_by('fitness_type')
    
    type_data = []
    for type_info in types:
        type_data.append({
            'value': type_info['fitness_type'],
            'label': dict(FitnessCenter.FITNESS_TYPE_CHOICES).get(type_info['fitness_type']),
            'count': type_info['count'],
            'average_rating': round(type_info['avg_rating'] or 0, 1)
        })
    
    return Response({
        'types': type_data,
        'total_centers': sum(t['count'] for t in type_data)
    })

@api_view(['GET'])
def nearby_fitness_centers(request):
    """Find fitness centers near a location"""
    lat = request.GET.get('latitude')
    lng = request.GET.get('longitude')
    radius = float(request.GET.get('radius', 5))  # Default 5km radius
    fitness_type = request.GET.get('fitness_type')
    
    if not lat or not lng:
        return Response(
            {'error': 'Latitude and longitude are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Simple distance calculation (not using PostGIS for simplicity)
        lat = float(lat)
        lng = float(lng)
        
        queryset = FitnessCenter.objects.select_related('provider').filter(
            provider__status='approved',
            provider__latitude__isnull=False,
            provider__longitude__isnull=False
        )
        
        if fitness_type:
            queryset = queryset.filter(fitness_type=fitness_type)
        
        # Filter by rough bounding box first (performance optimization)
        lat_delta = radius / 111.0
        lng_delta = radius / (111.0 * math.cos(math.radians(lat)))
        
        queryset = queryset.filter(
            provider__latitude__range=[lat - lat_delta, lat + lat_delta],
            provider__longitude__range=[lng - lng_delta, lng + lng_delta]
        )
        
        # Calculate exact distances and filter
        nearby_centers = []
        for center in queryset:
            if center.provider.latitude and center.provider.longitude:
                # Haversine formula for distance calculation
                distance = calculate_distance(
                    lat, lng,
                    float(center.provider.latitude), 
                    float(center.provider.longitude)
                )
                
                if distance <= radius:
                    serializer = FitnessCenterListSerializer(center)
                    center_data = serializer.data
                    center_data['distance'] = round(distance, 2)
                    nearby_centers.append(center_data)
        
        # Sort by distance
        nearby_centers.sort(key=lambda x: x['distance'])
        
        return Response({
            'centers': nearby_centers,
            'count': len(nearby_centers),
            'search_params': {
                'latitude': lat,
                'longitude': lng,
                'radius_km': radius,
                'fitness_type': fitness_type
            }
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    
    a = (math.sin(dLat/2) * math.sin(dLat/2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLon/2) * math.sin(dLon/2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance

@api_view(['POST'])
def search_fitness_centers(request):
    """Advanced search for fitness centers"""
    serializer = FitnessSearchSerializer(data=request.data)
    
    if serializer.is_valid():
        # Use the list view with validated search parameters
        # This could be enhanced to use the validated data more directly
        search_params = serializer.validated_data
        
        # Build queryset based on search parameters
        queryset = FitnessCenter.objects.select_related('provider').filter(
            provider__status='approved'
        )
        
        # Apply filters from search parameters
        for field, value in search_params.items():
            if field == 'fitness_type':
                queryset = queryset.filter(fitness_type=value)
            elif field == 'district':
                queryset = queryset.filter(provider__district=value)
            elif field == 'min_rating':
                queryset = queryset.filter(provider__average_rating__gte=value)
            elif field == 'max_price':
                queryset = queryset.filter(trial_class_price__lte=value)
            elif field in ['has_parking', 'has_shower_facilities', 'personal_training_available', 
                          'group_classes_available', 'trial_class_available']:
                queryset = queryset.filter(**{field: value})
        
        # Handle location-based search
        if 'latitude' in search_params and 'longitude' in search_params:
            lat = float(search_params['latitude'])
            lng = float(search_params['longitude'])
            radius = float(search_params.get('radius_km', 10))
            
            # Apply location filter (simplified)
            lat_delta = radius / 111.0
            lng_delta = radius / (111.0 * math.cos(math.radians(lat)))
            
            queryset = queryset.filter(
                provider__latitude__range=[lat - lat_delta, lat + lat_delta],
                provider__longitude__range=[lng - lng_delta, lng + lng_delta]
            )
        
        # Serialize results
        serializer = FitnessCenterListSerializer(queryset, many=True)
        
        return Response({
            'results': serializer.data,
            'count': queryset.count(),
            'search_parameters': search_params
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
