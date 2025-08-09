from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import FormView
import json
from datetime import datetime, date
from nutrition.models import Food, MealLog, FoodCategory, LocalFoodDatabase
from activity.models import ActivityLog
from providers.models import Provider, ProviderService
from personalization.models import UserProfile, RecommendationEngine
from search.services import ProviderSearchService
from search.models import SearchQuery, PopularSearch
from bookings.models import Booking, BookingAvailability


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'web/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        user = self.request.user
        
        # Get today's meals
        today_meals = MealLog.objects.filter(
            user=user, 
            log_date=today
        ).select_related('food')
        
        # Get today's activities
        today_activities = ActivityLog.objects.filter(
            user=user,
            started_at__date=today
        )
        
        # Get user profile and recommendations
        try:
            user_profile = UserProfile.objects.get(user=user)
            profile_completion = user_profile.profile_completion_percentage if hasattr(user_profile, 'profile_completion_percentage') else 0
        except UserProfile.DoesNotExist:
            user_profile = None
            profile_completion = 0
        
        # Get user's bookings
        user_bookings = Booking.objects.filter(user=user, booking_date__gte=today).order_by('booking_date')[:3]
        
        # Get recommendations
        recommendations = RecommendationEngine.get_meal_recommendations(user) if user_profile else []
        
        # Get popular searches
        popular_searches = PopularSearch.objects.all()[:5]
        
        # Get food categories and counts
        food_categories = FoodCategory.objects.all()[:5]
        total_foods = Food.objects.count()
        sri_lankan_foods = LocalFoodDatabase.objects.count()
        
        # Get provider statistics
        total_providers = Provider.objects.filter(status='approved').count()
        available_services = ProviderService.objects.count()
        
        # Calculate totals
        total_calories = sum(meal.food.calories * meal.quantity for meal in today_meals)
        total_activity_minutes = sum(activity.duration_minutes for activity in today_activities)
        
        # Calculate calories for each meal for template display
        for meal in today_meals:
            meal.total_calories = meal.food.calories * meal.quantity
        
        context.update({
            'today_meals': today_meals,
            'today_activities': today_activities,
            'total_calories': total_calories,
            'total_activity_minutes': total_activity_minutes,
            'today': today,
            'user_profile': user_profile,
            'profile_completion': profile_completion,
            'user_bookings': user_bookings,
            'recommendations': recommendations,
            'popular_searches': popular_searches,
            'food_categories': food_categories,
            'total_foods': total_foods,
            'sri_lankan_foods': sri_lankan_foods,
            'total_providers': total_providers,
            'available_services': available_services,
        })
        return context


class NutritionView(LoginRequiredMixin, TemplateView):
    template_name = 'web/nutrition.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_date = self.request.GET.get('date', date.today().isoformat())
        
        meals = MealLog.objects.filter(
            user=self.request.user,
            log_date=selected_date
        ).select_related('food').order_by('meal_type', 'logged_at')
        
        # Calculate totals for template
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        
        for meal in meals:
            meal.total_calories = meal.food.calories * meal.quantity
            meal.total_protein = meal.food.protein_g * meal.quantity
            meal.total_carbs = meal.food.carbs_g * meal.quantity
            meal.total_fat = meal.food.fat_g * meal.quantity
            total_calories += meal.total_calories
            total_protein += meal.total_protein
            total_carbs += meal.total_carbs
            total_fat += meal.total_fat
        
        # Get food categories and Sri Lankan foods
        food_categories = FoodCategory.objects.all()
        sri_lankan_foods = Food.objects.filter(localfooddatabase__isnull=False).select_related('localfooddatabase')[:10]
        foods = Food.objects.all().order_by('name')[:50]  # Limit for performance
        
        # Get recent searches for food suggestions
        recent_searches = SearchQuery.objects.filter(user=self.request.user).order_by('-created_at')[:5]
        
        context.update({
            'meals': meals,
            'foods': foods,
            'food_categories': food_categories,
            'sri_lankan_foods': sri_lankan_foods,
            'recent_searches': recent_searches,
            'selected_date': selected_date,
            'total_calories': total_calories,
            'total_protein': total_protein,
            'total_carbs': total_carbs,
            'total_fat': total_fat,
        })
        return context


class ActivityView(LoginRequiredMixin, TemplateView):
    template_name = 'web/activity.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_date = self.request.GET.get('date', date.today().isoformat())
        
        activities = ActivityLog.objects.filter(
            user=self.request.user,
            started_at__date=selected_date
        ).order_by('-started_at')
        
        context.update({
            'activities': activities,
            'selected_date': selected_date,
        })
        return context


class MealsProviderView(LoginRequiredMixin, TemplateView):
    template_name = 'web/meals_provider.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get search parameters
        search_query = self.request.GET.get('search', '')
        category = self.request.GET.get('category', '')
        district = self.request.GET.get('district', '')
        
        # Initialize search service
        search_service = ProviderSearchService()
        
        # Get all providers for now, filter by nutrition-related if no specific search
        if category or search_query:
            try:
                providers = search_service.search_providers(
                    query=search_query,
                    category=category,
                    district=district,
                    min_rating=0,
                    max_distance=50
                )
            except Exception:
                # Fallback if search service has issues
                providers = Provider.objects.filter(status='approved').select_related('user')[:20]
        else:
            # Show all providers if no filters
            providers = Provider.objects.all().select_related('user')[:20]
        
        # Get unique categories for filter - focusing on nutrition-related ones
        nutrition_categories_display = [
            ('nutritionist', 'Nutritionist'),
            ('millet_food', 'Healthy Food Shops'), 
            ('ayurveda', 'Ayurvedic Centers'),
            ('gym', 'Fitness Centers'),
        ]
        
        # Get unique districts
        districts = Provider.objects.values_list('district', flat=True).distinct().order_by('district')
        
        context.update({
            'providers': providers,
            'search_query': search_query,
            'selected_category': category,
            'selected_district': district,
            'categories': nutrition_categories_display,
            'districts': districts,
        })
        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'web/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get or create user profile
        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            user_profile = None
        
        # Get user's meal history
        recent_meals = MealLog.objects.filter(user=user).select_related('food').order_by('-logged_at')[:10]
        
        # Get user's activity history
        recent_activities = ActivityLog.objects.filter(user=user).order_by('-started_at')[:10]
        
        # Get user's bookings
        user_bookings = Booking.objects.filter(user=user).select_related('provider', 'service').order_by('-booking_date')[:10]
        
        # Get user's search history
        search_history = SearchQuery.objects.filter(user=user).order_by('-created_at')[:10]
        
        # Calculate some stats
        total_meals_logged = MealLog.objects.filter(user=user).count()
        total_activities_logged = ActivityLog.objects.filter(user=user).count()
        total_bookings_made = Booking.objects.filter(user=user).count()
        
        context.update({
            'user_profile': user_profile,
            'recent_meals': recent_meals,
            'recent_activities': recent_activities,
            'user_bookings': user_bookings,
            'search_history': search_history,
            'total_meals_logged': total_meals_logged,
            'total_activities_logged': total_activities_logged,
            'total_bookings_made': total_bookings_made,
        })
        return context


@method_decorator(csrf_exempt, name='dispatch')
class LogMealView(LoginRequiredMixin, CreateView):
    model = MealLog
    fields = ['food', 'quantity', 'meal_type', 'log_date']
    template_name = 'web/log_meal.html'
    success_url = reverse_lazy('nutrition')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Meal logged successfully!')
        return super().form_valid(form)


@method_decorator(csrf_exempt, name='dispatch')
class LogActivityView(LoginRequiredMixin, CreateView):
    model = ActivityLog
    fields = ['activity_type', 'duration_minutes', 'distance_km', 'calories_burned', 'started_at']
    template_name = 'web/log_activity.html'
    success_url = reverse_lazy('activity')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Activity logged successfully!')
        return super().form_valid(form)


@require_http_methods(["POST"])
def api_log_meal(request):
    try:
        data = json.loads(request.body)
        food = get_object_or_404(Food, id=data['food_id'])
        
        meal = MealLog.objects.create(
            user=request.user,
            food=food,
            quantity=data['quantity'],
            meal_type=data['meal_type'],
            log_date=data['log_date']
        )
        
        return JsonResponse({
            'success': True,
            'meal': {
                'id': meal.id,
                'food_name': meal.food.name,
                'quantity': meal.quantity,
                'meal_type': meal.meal_type,
                'calories': meal.food.calories * meal.quantity
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


class LoginView(FormView):
    template_name = 'web/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            messages.success(self.request, f'Welcome back, {user.username}!')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Invalid username or password.')
            return self.form_invalid(form)


@require_http_methods(["POST"])
def api_log_activity(request):
    try:
        data = json.loads(request.body)
        
        activity = ActivityLog.objects.create(
            user=request.user,
            activity_type=data['activity_type'],
            duration_minutes=data['duration_minutes'],
            distance_km=data.get('distance_km', 0),
            calories_burned=data.get('calories_burned', 0),
            started_at=data['started_at']
        )
        
        return JsonResponse({
            'success': True,
            'activity': {
                'id': activity.id,
                'activity_type': activity.activity_type,
                'duration_minutes': activity.duration_minutes,
                'calories_burned': activity.calories_burned
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

