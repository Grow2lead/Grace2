from django.contrib import admin
from django.utils.html import format_html
from .models import Provider, ProviderService, ProviderMedia

@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'category', 'district', 'status', 'is_verified', 'average_rating', 'total_bookings', 'created_at')
    list_filter = ('category', 'district', 'status', 'is_verified', 'accepts_online_bookings')
    search_fields = ('business_name', 'business_name_si', 'business_name_ta', 'email', 'phone', 'address')
    readonly_fields = ('slug', 'total_bookings', 'total_reviews', 'average_rating', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'business_name', 'business_name_si', 'business_name_ta', 'category', 'subcategory', 'status')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'whatsapp', 'website')
        }),
        ('Location', {
            'fields': ('address', 'city', 'district', 'postal_code', 'latitude', 'longitude')
        }),
        ('Business Details', {
            'fields': ('description', 'description_si', 'description_ta', 'operating_hours', 'amenities', 'pricing_info')
        }),
        ('Verification & Trust', {
            'fields': ('is_verified', 'verification_documents')
        }),
        ('Performance Metrics', {
            'fields': ('total_bookings', 'total_reviews', 'average_rating'),
            'classes': ('collapse',)
        }),
        ('Business Settings', {
            'fields': ('accepts_online_bookings', 'cancellation_policy')
        }),
        ('SEO & Marketing', {
            'fields': ('slug',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_providers', 'verify_providers', 'suspend_providers']
    
    def approve_providers(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f"Successfully approved {queryset.count()} providers.")
    approve_providers.short_description = "Approve selected providers"
    
    def verify_providers(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, f"Successfully verified {queryset.count()} providers.")
    verify_providers.short_description = "Verify selected providers"
    
    def suspend_providers(self, request, queryset):
        queryset.update(status='suspended')
        self.message_user(request, f"Successfully suspended {queryset.count()} providers.")
    suspend_providers.short_description = "Suspend selected providers"

@admin.register(ProviderService)
class ProviderServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'service_type', 'price', 'duration_minutes', 'max_participants', 'is_active')
    list_filter = ('service_type', 'is_active', 'provider__category')
    search_fields = ('name', 'name_si', 'name_ta', 'provider__business_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('provider', 'name', 'name_si', 'name_ta', 'service_type', 'description')
        }),
        ('Pricing & Duration', {
            'fields': ('price', 'currency', 'duration_minutes', 'max_participants')
        }),
        ('Availability', {
            'fields': ('is_bookable', 'is_active', 'sort_order')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProviderMedia)
class ProviderMediaAdmin(admin.ModelAdmin):
    list_display = ('provider', 'title', 'image_preview', 'is_featured', 'uploaded_at')
    list_filter = ('is_featured', 'uploaded_at')
    search_fields = ('provider__business_name', 'title')
    readonly_fields = ('uploaded_at', 'image_preview')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: 60px; object-fit: cover;" />', obj.image.url)
        return "No image"
    image_preview.short_description = "Preview"