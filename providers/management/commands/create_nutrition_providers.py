from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from providers.models import Provider, ProviderService

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample nutrition-focused providers'

    def handle(self, *args, **options):
        self.stdout.write('Creating nutrition-focused providers...')

        # Nutrition providers data
        providers_data = [
            {
                'business_name': 'Lanka Nutrition Center',
                'category': 'nutritionist',
                'description': 'Professional nutrition counseling and diet planning services. Specializing in weight management, diabetes management, and sports nutrition.',
                'address': '45 Galle Road, Colombo 03',
                'city': 'Colombo',
                'district': 'colombo',
                'phone': '+94 11 2345678',
                'email': 'info@lankanutrition.lk',
                'latitude': 6.9271,
                'longitude': 79.8612,
                'operating_hours': {
                    'monday': '08:00-17:00',
                    'tuesday': '08:00-17:00',
                    'wednesday': '08:00-17:00',
                    'thursday': '08:00-17:00',
                    'friday': '08:00-17:00',
                    'saturday': '09:00-13:00'
                },
                'services': [
                    {'name': 'Nutrition Consultation', 'service_type': 'consultation', 'duration_minutes': 60, 'price': 2500.00, 'description': 'One-on-one nutrition consultation'},
                    {'name': 'Diet Plan Creation', 'service_type': 'consultation', 'duration_minutes': 90, 'price': 4000.00, 'description': 'Customized diet plan creation'},
                    {'name': 'Weight Management Program', 'service_type': 'package', 'duration_minutes': 45, 'price': 3500.00, 'description': 'Comprehensive weight management program'},
                ]
            },
            {
                'business_name': 'Healthy Meals Colombo',
                'category': 'meal_delivery',
                'description': 'Fresh, healthy meal delivery service with customized meal plans. All meals prepared by certified nutritionists.',
                'address': '123 Baseline Road, Colombo 09',
                'city': 'Colombo',
                'district': 'colombo',
                'phone': '+94 77 1234567',
                'email': 'orders@healthymeals.lk',
                'latitude': 6.8905,
                'longitude': 79.8561,
                'operating_hours': {
                    'monday': '06:00-20:00',
                    'tuesday': '06:00-20:00',
                    'wednesday': '06:00-20:00',
                    'thursday': '06:00-20:00',
                    'friday': '06:00-20:00',
                    'saturday': '07:00-19:00',
                    'sunday': '08:00-18:00'
                },
                'services': [
                    {'name': 'Daily Meal Plan', 'service_type': 'package', 'duration_minutes': 0, 'price': 1500.00, 'description': 'Healthy daily meal delivery'},
                    {'name': 'Weekly Meal Package', 'service_type': 'package', 'duration_minutes': 0, 'price': 9500.00, 'description': 'Complete weekly meal package'},
                    {'name': 'Custom Diet Meals', 'service_type': 'package', 'duration_minutes': 0, 'price': 1800.00, 'description': 'Customized diet-specific meals'},
                ]
            },
            {
                'business_name': 'Dr. Silva Dietitian Clinic',
                'category': 'dietitian',
                'description': 'Clinical dietitian specializing in therapeutic nutrition for medical conditions. Expert in diabetes, heart disease, and digestive disorders.',
                'address': '78 Ward Place, Colombo 07',
                'city': 'Colombo',
                'district': 'colombo',
                'phone': '+94 11 2567890',
                'email': 'clinic@drsilva.lk',
                'latitude': 6.9147,
                'longitude': 79.8747,
                'operating_hours': {
                    'monday': '09:00-16:00',
                    'tuesday': '09:00-16:00',
                    'wednesday': '09:00-16:00',
                    'thursday': '09:00-16:00',
                    'friday': '09:00-14:00'
                },
                'services': [
                    {'name': 'Medical Nutrition Therapy', 'service_type': 'treatment', 'duration_minutes': 75, 'price': 5000.00, 'description': 'Clinical nutrition therapy for medical conditions'},
                    {'name': 'Diabetes Management Plan', 'service_type': 'consultation', 'duration_minutes': 90, 'price': 6000.00, 'description': 'Comprehensive diabetes diet planning'},
                    {'name': 'Heart-Healthy Diet Consultation', 'service_type': 'consultation', 'duration_minutes': 60, 'price': 4500.00, 'description': 'Specialized cardiac diet consultation'},
                ]
            },
            {
                'business_name': 'Green Leaf Organic Foods',
                'category': 'healthy_food',
                'description': 'Organic food store and juice bar offering fresh, locally-sourced produce and healthy meal options.',
                'address': '56 Havelock Road, Colombo 05',
                'city': 'Colombo',
                'district': 'colombo',
                'phone': '+94 76 9876543',
                'email': 'info@greenleaf.lk',
                'latitude': 6.8988,
                'longitude': 79.8590,
                'operating_hours': {
                    'monday': '07:00-19:00',
                    'tuesday': '07:00-19:00',
                    'wednesday': '07:00-19:00',
                    'thursday': '07:00-19:00',
                    'friday': '07:00-19:00',
                    'saturday': '08:00-18:00',
                    'sunday': '09:00-17:00'
                },
                'services': [
                    {'name': 'Fresh Juice Consultation', 'service_type': 'consultation', 'duration_minutes': 15, 'price': 800.00, 'description': 'Personalized fresh juice recommendations'},
                    {'name': 'Organic Meal Prep', 'service_type': 'package', 'duration_minutes': 0, 'price': 1200.00, 'description': 'Prepared organic meals'},
                    {'name': 'Nutrition Shopping Guide', 'service_type': 'consultation', 'duration_minutes': 30, 'price': 1500.00, 'description': 'Guided nutrition shopping tour'},
                ]
            },
            {
                'business_name': 'Kandy Wellness Nutrition',
                'category': 'nutritionist',
                'description': 'Holistic nutrition center combining modern nutrition science with traditional Ayurvedic principles.',
                'address': '23 Temple Street, Kandy',
                'city': 'Kandy',
                'district': 'kandy',
                'phone': '+94 81 2234567',
                'email': 'info@kandywellness.lk',
                'latitude': 7.2906,
                'longitude': 80.6337,
                'operating_hours': {
                    'monday': '08:30-17:30',
                    'tuesday': '08:30-17:30',
                    'wednesday': '08:30-17:30',
                    'thursday': '08:30-17:30',
                    'friday': '08:30-17:30',
                    'saturday': '09:00-15:00'
                },
                'services': [
                    {'name': 'Ayurvedic Nutrition Consultation', 'service_type': 'consultation', 'duration_minutes': 75, 'price': 3500.00, 'description': 'Traditional Ayurvedic nutrition consultation'},
                    {'name': 'Dosha-Based Diet Plan', 'service_type': 'consultation', 'duration_minutes': 90, 'price': 4500.00, 'description': 'Personalized diet plan based on Ayurvedic constitution'},
                    {'name': 'Herbal Nutrition Therapy', 'service_type': 'treatment', 'duration_minutes': 60, 'price': 3000.00, 'description': 'Herbal-based nutritional therapy'},
                ]
            },
            {
                'business_name': 'Galle Fresh Meals',
                'category': 'meal_delivery',
                'description': 'Southern Province meal delivery service featuring fresh seafood and traditional Sri Lankan healthy recipes.',
                'address': '12 Lighthouse Street, Galle',
                'city': 'Galle',
                'district': 'galle',
                'phone': '+94 91 2345678',
                'email': 'orders@gallefresh.lk',
                'latitude': 6.0329,
                'longitude': 80.2168,
                'operating_hours': {
                    'monday': '06:30-19:30',
                    'tuesday': '06:30-19:30',
                    'wednesday': '06:30-19:30',
                    'thursday': '06:30-19:30',
                    'friday': '06:30-19:30',
                    'saturday': '07:00-19:00',
                    'sunday': '08:00-18:00'
                },
                'services': [
                    {'name': 'Fresh Seafood Meals', 'service_type': 'package', 'duration_minutes': 0, 'price': 1600.00, 'description': 'Fresh daily seafood meal delivery'},
                    {'name': 'Traditional Healthy Curry Set', 'service_type': 'package', 'duration_minutes': 0, 'price': 1200.00, 'description': 'Traditional Sri Lankan healthy curry meals'},
                    {'name': 'Coastal Diet Package', 'service_type': 'package', 'duration_minutes': 0, 'price': 8500.00, 'description': 'Weekly coastal diet meal package'},
                ]
            }
        ]

        for provider_data in providers_data:
            services_data = provider_data.pop('services')
            
            # Create a user for the provider or use existing testuser
            user, _ = User.objects.get_or_create(
                username=f"provider_{provider_data['business_name'].lower().replace(' ', '_')}",
                defaults={
                    'email': provider_data['email'],
                    'first_name': provider_data['business_name'],
                }
            )
            
            provider_data['user'] = user
            
            provider, created = Provider.objects.get_or_create(
                business_name=provider_data['business_name'],
                defaults=provider_data
            )
            
            if created:
                self.stdout.write(f'Created provider: {provider.business_name}')
                
                # Create services for the provider
                for service_data in services_data:
                    service_data['provider'] = provider
                    ProviderService.objects.create(**service_data)
                    self.stdout.write(f'  - Added service: {service_data["name"]}')
            else:
                self.stdout.write(f'Provider already exists: {provider.business_name}')

        self.stdout.write(self.style.SUCCESS('Successfully created nutrition-focused providers!'))
