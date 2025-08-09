from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from providers.models import Provider, ProviderService, FitnessCenter
from bookings.models import Booking


class FitnessCentersView(LoginRequiredMixin, TemplateView):
    template_name = 'web/fitness_centers.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get search parameters
        search_query = self.request.GET.get('search', '')
        fitness_type = self.request.GET.get('fitness_type', '')
        district = self.request.GET.get('district', '')
        
        # Get fitness centers with filters
        fitness_centers = FitnessCenter.objects.select_related('provider').filter(
            provider__status='approved'
        )
        
        if fitness_type:
            fitness_centers = fitness_centers.filter(fitness_type=fitness_type)
        
        if district:
            fitness_centers = fitness_centers.filter(provider__district=district)
        
        if search_query:
            fitness_centers = fitness_centers.filter(
                provider__business_name__icontains=search_query
            )
        
        # Get statistics
        total_centers = FitnessCenter.objects.filter(provider__status='approved').count()
        gym_count = FitnessCenter.objects.filter(fitness_type='gym', provider__status='approved').count()
        zumba_count = FitnessCenter.objects.filter(fitness_type='zumba', provider__status='approved').count()
        
        # Get unique districts for filter
        districts = FitnessCenter.objects.select_related('provider').filter(
            provider__status='approved'
        ).values_list('provider__district', flat=True).distinct().order_by('provider__district')
        
        # Get fitness types for filter
        fitness_types = FitnessCenter.FITNESS_TYPE_CHOICES
        
        context.update({
            'fitness_centers': fitness_centers[:20],  # Limit for performance
            'search_query': search_query,
            'selected_fitness_type': fitness_type,
            'selected_district': district,
            'fitness_types': fitness_types,
            'districts': districts,
            'total_centers': total_centers,
            'gym_count': gym_count,
            'zumba_count': zumba_count,
        })
        return context


class FitnessCenterDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'web/fitness_center_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        center_id = kwargs.get('center_id')
        
        try:
            fitness_center = FitnessCenter.objects.select_related('provider').prefetch_related(
                'instructors', 'class_schedules', 'class_schedules__instructor'
            ).get(id=center_id, provider__status='approved')
            
            # Get services for this provider
            services = ProviderService.objects.filter(provider=fitness_center.provider, is_active=True)
            
            # Get user's bookings at this center
            user_bookings = Booking.objects.filter(
                user=self.request.user,
                provider=fitness_center.provider
            ).order_by('-booking_date')[:5]
            
            context.update({
                'fitness_center': fitness_center,
                'services': services,
                'user_bookings': user_bookings,
            })
            
        except FitnessCenter.DoesNotExist:
            context['error'] = 'Fitness center not found'
            
        return context

