from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class SearchQuery(models.Model):
    """Track search queries for analytics"""
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    query_text = models.CharField(max_length=500)
    filters_applied = models.JSONField(default=dict, help_text="Search filters used")
    results_count = models.PositiveIntegerField(default=0)
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['query_text']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Search: {self.query_text} ({self.results_count} results)"

class PopularSearch(models.Model):
    """Popular search terms and suggestions"""
    
    term = models.CharField(max_length=200, unique=True)
    search_count = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=50, blank=True)
    is_trending = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-search_count']
        indexes = [
            models.Index(fields=['search_count']),
            models.Index(fields=['is_trending']),
        ]
    
    def __str__(self):
        return f"{self.term} ({self.search_count} searches)"