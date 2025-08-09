from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from providers.models import Provider, ProviderService
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create Sri Lankan gym and Zumba centers with realistic data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of fitness centers to create (default: 50)'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        self.stdout.write('Creating Sri Lankan gym and Zumba centers...')
        
        # Function to create unique user for each provider
        def create_user_for_provider(business_name):
            """Create a unique user for each provider"""
            username = business_name.lower().replace(' ', '_').replace('\'', '').replace('&', 'and')[:30]
            email = f"{username}@fitness.lk"
            
            # Ensure username is unique
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}_{counter}"
                counter += 1
            
            return User.objects.create(
                username=username,
                email=email,
                first_name=business_name.split()[0],
                last_name='Center'
            )
        
        # Sri Lankan fitness center data
        gym_centers = [
            # Colombo District
            {
                'business_name': 'Fitness First Colombo',
                'business_name_si': 'ෆිට්නස් ෆර්ස්ට් කොළඹ',
                'category': 'gym',
                'subcategory': 'Premium Fitness Center',
                'district': 'colombo',
                'city': 'Colombo 03',
                'address': '123 Galle Road, Colombo 03',
                'latitude': Decimal('6.9271'),
                'longitude': Decimal('79.8612'),
                'description': 'Premium fitness center with state-of-the-art equipment, personal training, and group classes.',
                'amenities': ['Air Conditioning', 'Personal Training', 'Group Classes', 'Parking', 'Shower Facilities', 'Equipment Rental'],
                'services': [
                    {'name': 'Gym Membership', 'type': 'session', 'price': 8000, 'duration': 60},
                    {'name': 'Personal Training', 'type': 'session', 'price': 3500, 'duration': 60},
                    {'name': 'Group Fitness Class', 'type': 'class', 'price': 1200, 'duration': 45},
                ]
            },
            {
                'business_name': 'Gold\'s Gym Colombo',
                'business_name_si': 'ගෝල්ඩ්ස් ජිම් කොළඹ',
                'category': 'gym',
                'subcategory': 'International Franchise',
                'district': 'colombo',
                'city': 'Colombo 07',
                'address': '456 Independence Avenue, Colombo 07',
                'latitude': Decimal('6.9147'),
                'longitude': Decimal('79.8753'),
                'description': 'International fitness franchise with world-class facilities and certified trainers.',
                'amenities': ['Modern Equipment', 'CrossFit Area', 'Nutrition Counseling', 'Parking', 'Locker Rooms'],
                'services': [
                    {'name': 'Standard Membership', 'type': 'session', 'price': 12000, 'duration': 60},
                    {'name': 'CrossFit Session', 'type': 'class', 'price': 2000, 'duration': 60},
                    {'name': 'Nutrition Consultation', 'type': 'consultation', 'price': 4000, 'duration': 30},
                ]
            },
            {
                'business_name': 'Power Zone Gym',
                'business_name_si': 'පවර් සෝන් ජිම්',
                'category': 'gym',
                'subcategory': 'Strength Training',
                'district': 'colombo',
                'city': 'Nugegoda',
                'address': '789 High Level Road, Nugegoda',
                'latitude': Decimal('6.8649'),
                'longitude': Decimal('79.8997'),
                'description': 'Specialized strength training gym with powerlifting and bodybuilding focus.',
                'amenities': ['Free Weights', 'Powerlifting Platform', 'Cardio Equipment', 'Supplements Store'],
                'services': [
                    {'name': 'Gym Access', 'type': 'session', 'price': 6000, 'duration': 90},
                    {'name': 'Powerlifting Training', 'type': 'session', 'price': 3000, 'duration': 90},
                ]
            },
            {
                'business_name': 'Dance Fitness Lanka',
                'business_name_si': 'ඩාන්ස් ෆිට්නස් ලංකා',
                'category': 'zumba',
                'subcategory': 'Dance Fitness Studio',
                'district': 'colombo',
                'city': 'Colombo 05',
                'address': '321 Union Place, Colombo 05',
                'latitude': Decimal('6.9092'),
                'longitude': Decimal('79.8580'),
                'description': 'Premier dance fitness studio offering Zumba, aerobics, and dance classes.',
                'amenities': ['Sound System', 'Mirrors', 'Air Conditioning', 'Water Station', 'Parking'],
                'services': [
                    {'name': 'Zumba Class', 'type': 'class', 'price': 1500, 'duration': 60},
                    {'name': 'Aerobics Class', 'type': 'class', 'price': 1200, 'duration': 45},
                    {'name': 'Dance Workshop', 'type': 'workshop', 'price': 3500, 'duration': 120},
                ]
            },
            {
                'business_name': 'Rhythm & Motion Studio',
                'business_name_si': 'රිදම් ඇන්ඩ් මෝෂන් ස්ටුඩියෝ',
                'category': 'zumba',
                'subcategory': 'Dance & Fitness',
                'district': 'colombo',
                'city': 'Mount Lavinia',
                'address': '654 Galle Road, Mount Lavinia',
                'latitude': Decimal('6.8389'),
                'longitude': Decimal('79.8653'),
                'description': 'Modern dance studio specializing in Zumba, Latin dance, and fitness programs.',
                'amenities': ['Professional Dance Floor', 'Sound System', 'Changing Rooms', 'Parking'],
                'services': [
                    {'name': 'Zumba Gold', 'type': 'class', 'price': 1200, 'duration': 45},
                    {'name': 'Latin Dance', 'type': 'class', 'price': 1800, 'duration': 60},
                    {'name': 'Kids Zumba', 'type': 'class', 'price': 1000, 'duration': 30},
                ]
            },
            
            # Kandy District
            {
                'business_name': 'Kandy Fitness Center',
                'business_name_si': 'මහනුවර ෆිට්නස් මධ්‍යස්ථානය',
                'category': 'gym',
                'subcategory': 'Community Fitness',
                'district': 'kandy',
                'city': 'Kandy',
                'address': '147 Peradeniya Road, Kandy',
                'latitude': Decimal('7.2906'),
                'longitude': Decimal('80.6337'),
                'description': 'Community-focused fitness center serving Kandy and surrounding areas.',
                'amenities': ['Cardio Equipment', 'Weight Training', 'Group Classes', 'Parking'],
                'services': [
                    {'name': 'Monthly Membership', 'type': 'session', 'price': 5500, 'duration': 60},
                    {'name': 'Functional Training', 'type': 'class', 'price': 1000, 'duration': 45},
                ]
            },
            {
                'business_name': 'Hill Country Dance Studio',
                'business_name_si': 'කන්ද උඩරට නර්තන ශාලාව',
                'category': 'zumba',
                'subcategory': 'Dance Studio',
                'district': 'kandy',
                'city': 'Kandy',
                'address': '258 Temple Street, Kandy',
                'latitude': Decimal('7.2956'),
                'longitude': Decimal('80.6350'),
                'description': 'Traditional and modern dance classes including Zumba and cultural dances.',
                'amenities': ['Traditional Dance Space', 'Modern Equipment', 'Cultural Music'],
                'services': [
                    {'name': 'Zumba Class', 'type': 'class', 'price': 1200, 'duration': 60},
                    {'name': 'Cultural Dance', 'type': 'class', 'price': 1500, 'duration': 90},
                ]
            },
            
            # Gampaha District
            {
                'business_name': 'Negombo Beach Fitness',
                'business_name_si': 'මීගමුව වෙරළ ෆිට්නස්',
                'category': 'gym',
                'subcategory': 'Beach Fitness',
                'district': 'gampaha',
                'city': 'Negombo',
                'address': '369 Lewis Place, Negombo',
                'latitude': Decimal('7.2084'),
                'longitude': Decimal('79.8380'),
                'description': 'Beachside fitness center with outdoor training options and sea views.',
                'amenities': ['Outdoor Training Area', 'Beach Access', 'Equipment Rental', 'Parking'],
                'services': [
                    {'name': 'Beach Workout', 'type': 'session', 'price': 2500, 'duration': 60},
                    {'name': 'Indoor Gym', 'type': 'session', 'price': 4500, 'duration': 60},
                ]
            },
            {
                'business_name': 'Groove Studio Gampaha',
                'business_name_si': 'ග්‍රූව් ස්ටුඩියෝ ගම්පහ',
                'category': 'zumba',
                'subcategory': 'Dance & Fitness',
                'district': 'gampaha',
                'city': 'Gampaha',
                'address': '741 Colombo Road, Gampaha',
                'latitude': Decimal('7.0873'),
                'longitude': Decimal('80.0142'),
                'description': 'Energetic dance studio offering various dance fitness programs.',
                'amenities': ['Spring Floor', 'Sound System', 'Air Conditioning'],
                'services': [
                    {'name': 'Zumba Fitness', 'type': 'class', 'price': 1000, 'duration': 60},
                    {'name': 'Dance Cardio', 'type': 'class', 'price': 1200, 'duration': 45},
                ]
            },
            
            # Galle District
            {
                'business_name': 'Southern Fitness Hub',
                'business_name_si': 'දක්ෂිණ ෆිට්නස් මධ්‍යස්ථානය',
                'category': 'gym',
                'subcategory': 'Multi-purpose Fitness',
                'district': 'galle',
                'city': 'Galle',
                'address': '852 Matara Road, Galle',
                'latitude': Decimal('6.0535'),
                'longitude': Decimal('80.2210'),
                'description': 'Complete fitness facility serving the Southern Province with modern equipment.',
                'amenities': ['Modern Gym Equipment', 'Swimming Pool', 'Sauna', 'Parking', 'Cafe'],
                'services': [
                    {'name': 'Full Access Membership', 'type': 'session', 'price': 7500, 'duration': 120},
                    {'name': 'Swimming + Gym', 'type': 'session', 'price': 6000, 'duration': 90},
                    {'name': 'Aqua Fitness', 'type': 'class', 'price': 1800, 'duration': 45},
                ]
            },
            {
                'business_name': 'Galle Fort Dance Academy',
                'business_name_si': 'ගාල්ල කොටුව නර්තන ඇකඩමිය',
                'category': 'zumba',
                'subcategory': 'Historic Dance Studio',
                'district': 'galle',
                'city': 'Galle Fort',
                'address': '963 Church Street, Galle Fort',
                'latitude': Decimal('6.0264'),
                'longitude': Decimal('80.2170'),
                'description': 'Historic dance academy in Galle Fort offering traditional and modern dance classes.',
                'amenities': ['Historic Building', 'Traditional Setting', 'Cultural Programs'],
                'services': [
                    {'name': 'Zumba by the Fort', 'type': 'class', 'price': 1500, 'duration': 60},
                    {'name': 'Cultural Fusion Dance', 'type': 'class', 'price': 2000, 'duration': 75},
                ]
            },
        ]
        
        zumba_centers = [
            {
                'business_name': 'Zumba Central Colombo',
                'business_name_si': 'සුම්බා සෙන්ට්‍රල් කොළඹ',
                'category': 'zumba',
                'subcategory': 'Zumba Specialist',
                'district': 'colombo',
                'city': 'Colombo 06',
                'address': '159 Bauddhaloka Mawatha, Colombo 06',
                'latitude': Decimal('6.8916'),
                'longitude': Decimal('79.8550'),
                'description': 'Dedicated Zumba studio with certified instructors and high-energy classes.',
                'amenities': ['Professional Sound System', 'Sprung Dance Floor', 'Air Conditioning', 'Water Bar'],
                'services': [
                    {'name': 'Zumba Fitness', 'type': 'class', 'price': 1200, 'duration': 60},
                    {'name': 'Zumba Toning', 'type': 'class', 'price': 1400, 'duration': 60},
                    {'name': 'Aqua Zumba', 'type': 'class', 'price': 2000, 'duration': 45},
                ]
            },
            {
                'business_name': 'Latin Groove Studio',
                'business_name_si': 'ලැටින් ග්‍රූව් ස්ටුඩියෝ',
                'category': 'zumba',
                'subcategory': 'Latin Dance & Fitness',
                'district': 'colombo',
                'city': 'Rajagiriya',
                'address': '852 Kotte Road, Rajagiriya',
                'latitude': Decimal('6.9077'),
                'longitude': Decimal('79.8990'),
                'description': 'Specialized Latin dance and Zumba studio with authentic music and moves.',
                'amenities': ['Latin Music Collection', 'Professional Instructors', 'Cultural Events'],
                'services': [
                    {'name': 'Salsa Zumba', 'type': 'class', 'price': 1600, 'duration': 60},
                    {'name': 'Bachata Fitness', 'type': 'class', 'price': 1500, 'duration': 60},
                    {'name': 'Merengue Classes', 'type': 'class', 'price': 1400, 'duration': 45},
                ]
            },
            {
                'business_name': 'Movement Studio Dehiwala',
                'business_name_si': 'මූව්මන්ට් ස්ටුඩියෝ දෙහිවල',
                'category': 'zumba',
                'subcategory': 'Movement & Dance',
                'district': 'colombo',
                'city': 'Dehiwala',
                'address': '741 Galle Road, Dehiwala',
                'latitude': Decimal('6.8515'),
                'longitude': Decimal('79.8695'),
                'description': 'Creative movement studio focusing on dance fitness and wellness.',
                'amenities': ['Multiple Studios', 'Wellness Programs', 'Community Events'],
                'services': [
                    {'name': 'Zumba Strong', 'type': 'class', 'price': 1800, 'duration': 60},
                    {'name': 'Dance Cardio', 'type': 'class', 'price': 1300, 'duration': 45},
                    {'name': 'Wellness Workshop', 'type': 'workshop', 'price': 4000, 'duration': 120},
                ]
            },
        ]
        
        # Additional gym centers for other districts
        more_gyms = [
            {
                'business_name': 'Anuradhapura Fitness Zone',
                'business_name_si': 'අනුරාධපුර ෆිට්නස් සෝනය',
                'category': 'gym',
                'subcategory': 'Community Gym',
                'district': 'anuradhapura',
                'city': 'Anuradhapura',
                'address': '147 Maithripala Senanayake Mawatha, Anuradhapura',
                'latitude': Decimal('8.3114'),
                'longitude': Decimal('80.4037'),
                'description': 'Modern fitness facility in the ancient city with traditional values.',
                'amenities': ['Basic Equipment', 'Group Classes', 'Parking'],
                'services': [
                    {'name': 'Basic Membership', 'type': 'session', 'price': 4000, 'duration': 60},
                    {'name': 'Morning Fitness', 'type': 'class', 'price': 800, 'duration': 45},
                ]
            },
            {
                'business_name': 'Kurunegala Power Gym',
                'business_name_si': 'කුරුනෑගල පවර් ජිම්',
                'category': 'gym',
                'subcategory': 'Strength Training',
                'district': 'kurunegala',
                'city': 'Kurunegala',
                'address': '369 Colombo Road, Kurunegala',
                'latitude': Decimal('7.4863'),
                'longitude': Decimal('80.3647'),
                'description': 'Strength-focused gym serving the North Western Province.',
                'amenities': ['Weight Training', 'Cardio Section', 'Personal Training'],
                'services': [
                    {'name': 'Strength Training', 'type': 'session', 'price': 3500, 'duration': 90},
                    {'name': 'Cardio Session', 'type': 'session', 'price': 2500, 'duration': 45},
                ]
            },
            {
                'business_name': 'Jaffna Wellness Center',
                'business_name_si': 'යාපනය සුවතා මධ්‍යස්ථානය',
                'business_name_ta': 'யாழ்ப்பாண நல்வாழ்வு மையம்',
                'category': 'gym',
                'subcategory': 'Wellness & Fitness',
                'district': 'jaffna',
                'city': 'Jaffna',
                'address': '258 Hospital Road, Jaffna',
                'latitude': Decimal('9.6615'),
                'longitude': Decimal('80.0255'),
                'description': 'Comprehensive wellness center with fitness and health programs.',
                'amenities': ['Bilingual Staff', 'Cultural Sensitivity', 'Health Screening'],
                'services': [
                    {'name': 'Wellness Program', 'type': 'session', 'price': 5000, 'duration': 75},
                    {'name': 'Traditional Exercise', 'type': 'class', 'price': 1200, 'duration': 60},
                ]
            },
        ]
        
        all_centers = gym_centers + zumba_centers + more_gyms
        
        created_count = 0
        for center_data in all_centers[:count]:
            try:
                # Create provider
                services_data = center_data.pop('services', [])
                
                # Set default operating hours
                center_data['operating_hours'] = {
                    'monday': {'open': '06:00', 'close': '22:00'},
                    'tuesday': {'open': '06:00', 'close': '22:00'},
                    'wednesday': {'open': '06:00', 'close': '22:00'},
                    'thursday': {'open': '06:00', 'close': '22:00'},
                    'friday': {'open': '06:00', 'close': '22:00'},
                    'saturday': {'open': '07:00', 'close': '21:00'},
                    'sunday': {'open': '08:00', 'close': '20:00'},
                }
                
                # Create unique user for this provider
                center_data['user'] = create_user_for_provider(center_data['business_name'])
                center_data['email'] = f"info@{center_data['business_name'].lower().replace(' ', '').replace('\'', '')}.lk"
                center_data['phone'] = f"+94{random.randint(11, 77)}{random.randint(1000000, 9999999)}"
                center_data['status'] = 'approved'
                center_data['is_verified'] = True
                center_data['accepts_online_bookings'] = True
                
                provider, created = Provider.objects.get_or_create(
                    business_name=center_data['business_name'],
                    defaults=center_data
                )
                
                if created:
                    # Create services for the provider
                    for service_data in services_data:
                        ProviderService.objects.create(
                            provider=provider,
                            name=service_data['name'],
                            service_type=service_data['type'],
                            description=f"{service_data['name']} at {provider.business_name}",
                            price=Decimal(str(service_data['price'])),
                            duration_minutes=service_data['duration'],
                            max_participants=20 if service_data['type'] == 'class' else 1,
                        )
                    
                    created_count += 1
                    self.stdout.write(f"Created: {provider.business_name}")
                else:
                    self.stdout.write(f"Already exists: {provider.business_name}")
                    
            except Exception as e:
                self.stderr.write(f"Error creating {center_data.get('business_name', 'Unknown')}: {str(e)}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} fitness centers out of {len(all_centers[:count])} attempted.'
            )
        )
