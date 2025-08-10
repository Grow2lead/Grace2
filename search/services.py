from django.db.models import Q, F, Case, When, Value, FloatField, Count
from math import radians, cos, sin, asin, sqrt
from providers.models import Provider

class ProviderSearchService:
    """Advanced search service for providers"""
    
    def __init__(self):
        self.base_queryset = Provider.objects.filter(
            status='approved'
        ).select_related('user').prefetch_related('media', 'services')
    
    def search_providers(self, query_params, user_lat=None, user_lng=None):
        """Advanced provider search with multiple filters"""
        queryset = self.base_queryset
        
        # Text search
        search_query = query_params.get('q', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(business_name__icontains=search_query) |
                Q(business_name_si__icontains=search_query) |
                Q(business_name_ta__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(services__name__icontains=search_query)
            ).distinct()
        
        # Category filter
        category = query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Location filters
        district = query_params.get('district')
        if district:
            queryset = queryset.filter(district=district)
        
        city = query_params.get('city')
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        # Distance-based search
        if user_lat and user_lng:
            radius_km = float(query_params.get('radius', 10))
            queryset = self._filter_by_distance(queryset, user_lat, user_lng, radius_km)
        
        # Rating filter
        min_rating = query_params.get('min_rating')
        if min_rating:
            queryset = queryset.filter(average_rating__gte=float(min_rating))
        
        # Verification filter
        verified_only = query_params.get('verified_only')
        if verified_only and verified_only.lower() == 'true':
            queryset = queryset.filter(is_verified=True)
        
        # Online booking filter
        online_booking = query_params.get('online_booking')
        if online_booking and online_booking.lower() == 'true':
            queryset = queryset.filter(accepts_online_bookings=True)
        
        # Sorting
        sort_by = query_params.get('sort_by', 'relevance')
        if sort_by == 'rating':
            queryset = queryset.order_by('-average_rating', '-total_reviews')
        elif sort_by == 'reviews':
            queryset = queryset.order_by('-total_reviews', '-average_rating')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        else:  # relevance (default)
            queryset = queryset.annotate(
                relevance_score=Case(
                    When(is_verified=True, then=Value(2.0)),
                    default=Value(1.0),
                    output_field=FloatField()
                ) * F('average_rating')
            ).order_by('-relevance_score', '-total_reviews')
        
        return queryset
    
    def _filter_by_distance(self, queryset, user_lat, user_lng, radius_km):
        """Filter providers within specified radius"""
        lat_range = radius_km / 111.0  # Rough km per degree latitude
        lng_range = radius_km / (111.0 * cos(radians(user_lat)))
        
        return queryset.filter(
            latitude__isnull=False,
            longitude__isnull=False,
            latitude__range=[user_lat - lat_range, user_lat + lat_range],
            longitude__range=[user_lng - lng_range, user_lng + lng_range]
        )
    
    def calculate_distance(self, provider_lat, provider_lng, user_lat, user_lng):
        """Calculate distance using Haversine formula"""
        if not all([provider_lat, provider_lng, user_lat, user_lng]):
            return None
        
        lat1, lng1, lat2, lng2 = map(radians, [float(user_lat), float(user_lng), 
                                              float(provider_lat), float(provider_lng)])
        
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * asin(sqrt(a))
        
        return round(c * 6371, 2)  # Earth's radius in km



