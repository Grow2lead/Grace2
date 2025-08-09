from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('providers/', views.provider_search, name='provider-search'),
    path('providers/map/', views.provider_map_view, name='provider-map'),
    path('suggestions/', views.search_suggestions, name='search-suggestions'),
    path('filters/', views.search_filters, name='search-filters'),
]

