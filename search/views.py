from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count
from providers.models import Provider
from providers.serializers import ProviderSearchSerializer
from .models import SearchQuery, PopularSearch
from .services import ProviderSearchService

class SearchResultsPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def provider_search(request):
    """Advanced provider search endpoint"""
    try:
        # Get user location if provided
        user_lat = request.GET.get('lat')
        user_lng = request.GET.get('lng')
        if user_lat:
            user_lat = float(user_lat)
        if user_lng:
            user_lng = float(user_lng)
        
        # Perform search
        search_service = ProviderSearchService()
        queryset = search_service.search_providers(request.GET, user_lat, user_lng)
        
        # Calculate distances and serialize
        providers = []
        for provider in queryset:
            provider_data = ProviderSearchSerializer(provider, context={'request': request}).data
            
            if user_lat and user_lng and provider.latitude and provider.longitude:
                distance = search_service.calculate_distance(
                    provider.latitude, provider.longitude, user_lat, user_lng
                )
                provider_data['distance'] = distance
            
            providers.append(provider_data)
        
        # Sort by distance if requested
        sort_by = request.GET.get('sort_by')
        if sort_by == 'distance' and user_lat and user_lng:
            providers = sorted(providers, key=lambda x: x.get('distance') or float('inf'))
        
        # Pagination
        paginator = SearchResultsPagination()
        page = paginator.paginate_queryset(providers, request)
        
        # Log search query
        if request.GET.get('q'):
            SearchQuery.objects.create(
                user=request.user if request.user.is_authenticated else None,
                query_text=request.GET.get('q', ''),
                filters_applied={
                    'category': request.GET.get('category'),
                    'district': request.GET.get('district'),
                    'min_rating': request.GET.get('min_rating'),
                },
                results_count=len(providers),
                location_lat=user_lat,
                location_lng=user_lng
            )
        
        return paginator.get_paginated_response(page)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def provider_map_view(request):
    """Get providers for map display"""
    try:
        search_service = ProviderSearchService()
        queryset = search_service.search_providers(request.GET)
        
        queryset = queryset.filter(
            latitude__isnull=False,
            longitude__isnull=False
        )[:100]
        
        map_data = []
        for provider in queryset:
            featured_media = provider.media.filter(is_featured=True).first()
            map_data.append({
                'id': provider.id,
                'slug': provider.slug,
                'name': provider.business_name,
                'category': provider.category,
                'lat': float(provider.latitude),
                'lng': float(provider.longitude),
                'rating': float(provider.average_rating),
                'reviews': provider.total_reviews,
                'verified': provider.is_verified,
                'image': featured_media.image.url if featured_media else None
            })
        
        return Response({
            'providers': map_data,
            'total': len(map_data)
        })
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def search_suggestions(request):
    """Get search suggestions"""
    query = request.GET.get('q', '').strip()
    suggestions = []
    
    if query:
        # Provider name suggestions
        provider_suggestions = Provider.objects.filter(
            status='approved',
            business_name__icontains=query
        ).values_list('business_name', flat=True)[:5]
        
        suggestions.extend([
            {'text': name, 'type': 'provider'} 
            for name in provider_suggestions
        ])
        
        # Category suggestions
        category_matches = [
            (value, label) for value, label in Provider.CATEGORY_CHOICES 
            if query.lower() in label.lower()
        ]
        suggestions.extend([
            {'text': label, 'type': 'category', 'value': value}
            for value, label in category_matches
        ])
    
    # Popular searches
    popular = PopularSearch.objects.filter(is_trending=True)[:10]
    popular_searches = [
        {'text': p.term, 'type': 'popular', 'count': p.search_count}
        for p in popular
    ]
    
    return Response({
        'suggestions': suggestions[:10],
        'popular_searches': popular_searches
    })

@api_view(['GET'])
def search_filters(request):
    """Get available search filters"""
    # Categories with counts
    categories = Provider.objects.filter(status='approved').values('category').annotate(
        count=Count('id')
    ).order_by('category')
    
    category_filters = [
        {
            'value': cat['category'],
            'label': dict(Provider.CATEGORY_CHOICES).get(cat['category'], cat['category']),
            'count': cat['count']
        }
        for cat in categories
    ]
    
    # Districts with counts
    districts = Provider.objects.filter(status='approved').values('district').annotate(
        count=Count('id')
    ).order_by('district')
    
    district_filters = [
        {
            'value': dist['district'],
            'label': dict(Provider.DISTRICT_CHOICES).get(dist['district'], dist['district']),
            'count': dist['count']
        }
        for dist in districts
    ]
    
    return Response({
        'categories': category_filters,
        'districts': district_filters,
        'rating_options': [
            {'value': 4.5, 'label': '4.5+ Stars'},
            {'value': 4.0, 'label': '4.0+ Stars'},
            {'value': 3.5, 'label': '3.5+ Stars'},
            {'value': 3.0, 'label': '3.0+ Stars'},
        ]
    })
