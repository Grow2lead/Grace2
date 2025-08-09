from django.urls import path
from . import views

app_name = 'providers'

urlpatterns = [
    # Provider listing and search
    path('', views.ProviderListView.as_view(), name='list'),
    path('categories/', views.provider_categories, name='categories'),
    path('districts/', views.provider_districts, name='districts'),
    path('featured/', views.featured_providers, name='featured'),
    path('stats/', views.provider_stats, name='stats'),
    
    # Provider registration and profile management
    path('register/', views.ProviderRegistrationView.as_view(), name='register'),
    path('profile/', views.ProviderProfileView.as_view(), name='profile'),
    
    # Provider services
    path('services/', views.ProviderServiceListView.as_view(), name='my-services'),
    path('services/<int:pk>/', views.ProviderServiceDetailView.as_view(), name='service-detail'),
    
    # Media management
    path('media/upload/', views.upload_provider_media, name='upload-media'),
    path('media/<int:media_id>/delete/', views.delete_provider_media, name='delete-media'),
    
    # Public provider detail and services
    path('<slug:slug>/', views.ProviderDetailView.as_view(), name='detail'),
    path('<slug:provider_slug>/services/', views.ProviderServiceListView.as_view(), name='services'),
]
