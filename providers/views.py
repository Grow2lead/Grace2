from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from .models import Provider, ProviderService, ProviderMedia
from .serializers import (
    ProviderListSerializer, ProviderDetailSerializer, ProviderRegistrationSerializer,
    ProviderUpdateSerializer, ProviderServiceSerializer, ProviderServiceCreateSerializer,
    ProviderSearchSerializer
)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 50

class ProviderListView(generics.ListAPIView):
    """List all approved providers"""
    serializer_class = ProviderListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'district', 'is_verified']
    search_fields = ['business_name', 'business_name_si', 'business_name_ta', 'description']
    ordering_fields = ['average_rating', 'total_reviews', 'created_at']
    ordering = ['-average_rating', '-total_reviews']
    
    def get_queryset(self):
        return Provider.objects.filter(status='approved').select_related('user').prefetch_related('media')

class ProviderDetailView(generics.RetrieveAPIView):
    """Get detailed provider information"""
    serializer_class = ProviderDetailSerializer
    lookup_field = 'slug'
    
    def get_queryset(self):
        return Provider.objects.filter(status='approved').select_related('user').prefetch_related(
            'services', 'media'
        )

class ProviderRegistrationView(generics.CreateAPIView):
    """Register as a new provider"""
    serializer_class = ProviderRegistrationSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        # Check if user already has a provider profile
        if hasattr(request.user, 'provider_profile'):
            return Response({
                'error': 'You already have a provider profile'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        provider = serializer.save()
        
        return Response({
            'message': 'Provider registration submitted successfully. Your profile is under review.',
            'provider_id': provider.id,
            'status': provider.status
        }, status=status.HTTP_201_CREATED)

class ProviderProfileView(generics.RetrieveUpdateAPIView):
    """Get or update own provider profile"""
    serializer_class = ProviderDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return get_object_or_404(Provider, user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProviderUpdateSerializer
        return ProviderDetailSerializer

class ProviderServiceListView(generics.ListCreateAPIView):
    """List or create services for a provider"""
    serializer_class = ProviderServiceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        provider_slug = self.kwargs.get('provider_slug')
        if provider_slug:
            provider = get_object_or_404(Provider, slug=provider_slug, status='approved')
            return provider.services.filter(is_active=True)
        else:
            # Return current user's provider services
            provider = get_object_or_404(Provider, user=self.request.user)
            return provider.services.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProviderServiceCreateSerializer
        return ProviderServiceSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.method == 'POST':
            provider = get_object_or_404(Provider, user=self.request.user)
            context['provider'] = provider
        return context

class ProviderServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a specific service"""
    serializer_class = ProviderServiceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        provider = get_object_or_404(Provider, user=self.request.user)
        return provider.services.all()

@api_view(['GET'])
def provider_categories(request):
    """Get all provider categories with counts"""
    categories = Provider.objects.filter(status='approved').values('category').annotate(
        count=Count('id'),
        avg_rating=Avg('average_rating')
    ).order_by('category')
    
    category_data = []
    for cat in categories:
        category_info = {
            'value': cat['category'],
            'label': dict(Provider.CATEGORY_CHOICES).get(cat['category'], cat['category']),
            'count': cat['count'],
            'average_rating': round(cat['avg_rating'] or 0, 1)
        }
        category_data.append(category_info)
    
    return Response({
        'categories': category_data,
        'total_providers': Provider.objects.filter(status='approved').count()
    })

@api_view(['GET'])
def provider_districts(request):
    """Get all districts with provider counts"""
    districts = Provider.objects.filter(status='approved').values('district').annotate(
        count=Count('id')
    ).order_by('district')
    
    district_data = []
    for dist in districts:
        district_info = {
            'value': dist['district'],
            'label': dict(Provider.DISTRICT_CHOICES).get(dist['district'], dist['district']),
            'count': dist['count']
        }
        district_data.append(district_info)
    
    return Response({
        'districts': district_data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_provider_media(request):
    """Upload media for provider"""
    try:
        provider = get_object_or_404(Provider, user=request.user)
        
        if 'image' not in request.FILES:
            return Response({
                'error': 'No image file provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        media = ProviderMedia.objects.create(
            provider=provider,
            image=request.FILES['image'],
            title=request.data.get('title', ''),
            is_featured=request.data.get('is_featured', False)
        )
        
        return Response({
            'id': media.id,
            'image_url': request.build_absolute_uri(media.image.url),
            'title': media.title,
            'is_featured': media.is_featured
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_provider_media(request, media_id):
    """Delete provider media"""
    try:
        provider = get_object_or_404(Provider, user=request.user)
        media = get_object_or_404(ProviderMedia, id=media_id, provider=provider)
        media.delete()
        
        return Response({
            'message': 'Media deleted successfully'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def featured_providers(request):
    """Get featured providers"""
    featured = Provider.objects.filter(
        status='approved',
        is_verified=True
    ).order_by('-average_rating', '-total_reviews')[:6]
    
    serializer = ProviderListSerializer(featured, many=True, context={'request': request})
    return Response({
        'featured_providers': serializer.data
    })

@api_view(['GET'])
def provider_stats(request):
    """Get provider statistics for dashboard"""
    stats = {
        'total_providers': Provider.objects.filter(status='approved').count(),
        'verified_providers': Provider.objects.filter(status='approved', is_verified=True).count(),
        'categories': Provider.objects.filter(status='approved').values_list('category', flat=True).distinct().count(),
        'average_rating': Provider.objects.filter(status='approved').aggregate(
            avg=Avg('average_rating')
        )['avg'] or 0
    }
    
    # Category breakdown
    category_breakdown = Provider.objects.filter(status='approved').values('category').annotate(
        count=Count('id')
    ).order_by('-count')
    
    stats['category_breakdown'] = [
        {
            'category': dict(Provider.CATEGORY_CHOICES).get(item['category'], item['category']),
            'count': item['count']
        }
        for item in category_breakdown
    ]
    
    return Response(stats)