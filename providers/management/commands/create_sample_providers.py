from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from providers.models import Provider, ProviderService
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample providers for testing the marketplace'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample providers...')

        # Sample provider data for Sri Lankan wellness marketplace
        sample_providers = [
            {
                'user_data': {'username': 'greenyoga_colombo', 'email': 'info@greenyoga.lk', 'first_name': 'Green', 'last_name': 'Yoga'},
                'provider_data': {
                    'business_name': 'Green Yoga Studio',
                    'business_name_si': 'ග්‍රීන් යෝගා ස්ටුඩියෝ',
                    'business_name_ta': 'கிரீன் யோகா ஸ்டுடியோ',
                    'category': 'yoga',
                    'email': 'info@greenyoga.lk',
                    'phone': '+94771234567',
                    'whatsapp': '+94771234567',
                    'address': '123 Galle Road, Bambalapitiya',
                    'city': 'Colombo',
                    'district': 'colombo',
                    'postal_code': '00400',
                    'latitude': Decimal('6.8935'),
                    'longitude': Decimal('79.8500'),
                    'description': 'Premier yoga studio in Colombo offering traditional and modern yoga practices. Our experienced instructors guide you through various yoga styles including Hatha, Vinyasa, and Ashtanga.',
                    'description_si': 'කොළඹ හි ප්‍රමුඛ යෝගා ශාලාව සම්ප්‍රදායික හා නවීන යෝගා ක්‍රම ඉදිරිපත් කරයි.',
                    'description_ta': 'கொழும்பில் உள்ள முன்னணி யோகா நிலையம் பாரம்பரிய மற்றும் நவீன யோகா பயிற்சிகளை வழங்குகிறது.',
                    'operating_hours': {
                        'monday': {'open': '06:00', 'close': '21:00'},
                        'tuesday': {'open': '06:00', 'close': '21:00'},
                        'wednesday': {'open': '06:00', 'close': '21:00'},
                        'thursday': {'open': '06:00', 'close': '21:00'},
                        'friday': {'open': '06:00', 'close': '21:00'},
                        'saturday': {'open': '07:00', 'close': '19:00'},
                        'sunday': {'open': '07:00', 'close': '19:00'},
                    },
                    'amenities': ['Air Conditioning', 'Parking', 'Changing Rooms', 'Yoga Mats', 'Meditation Hall'],
                    'status': 'approved',
                    'is_verified': True,
                    'average_rating': Decimal('4.8'),
                    'total_reviews': 45,
                    'total_bookings': 120,
                    'accepts_online_bookings': True,
                    'cancellation_policy': 'Free cancellation up to 2 hours before class time.',
                },
                'services': [
                    {
                        'name': 'Hatha Yoga Class',
                        'name_si': 'හත යෝගා පන්තිය',
                        'name_ta': 'ஹத யோகா வகுப்பு',
                        'service_type': 'class',
                        'description': 'Gentle yoga practice focusing on basic postures and breathing.',
                        'price': Decimal('1500.00'),
                        'duration_minutes': 60,
                        'max_participants': 15,
                    },
                    {
                        'name': 'Private Yoga Session',
                        'name_si': 'පුද්ගලික යෝගා සැසිය',
                        'name_ta': 'தனிப்பட்ட யோகா அமர்வு',
                        'service_type': 'session',
                        'description': 'One-on-one personalized yoga instruction.',
                        'price': Decimal('5000.00'),
                        'duration_minutes': 90,
                        'max_participants': 1,
                    }
                ]
            },
            {
                'user_data': {'username': 'fitnessfirst_gampaha', 'email': 'contact@fitnessfirst.lk', 'first_name': 'Fitness', 'last_name': 'First'},
                'provider_data': {
                    'business_name': 'Fitness First Gym',
                    'business_name_si': 'ෆිට්නස් ෆර්ස්ට් ජිම්',
                    'business_name_ta': 'ஃபிட்னஸ் ஃபர்ஸ்ட் ஜிம்',
                    'category': 'gym',
                    'email': 'contact@fitnessfirst.lk',
                    'phone': '+94712345678',
                    'whatsapp': '+94712345678',
                    'address': '456 Kandy Road, Kiribathgoda',
                    'city': 'Kiribathgoda',
                    'district': 'gampaha',
                    'postal_code': '11600',
                    'latitude': Decimal('6.9822'),
                    'longitude': Decimal('79.9294'),
                    'description': 'State-of-the-art fitness center with modern equipment, professional trainers, and comprehensive fitness programs.',
                    'description_si': 'නවීන උපකරණ, වෘත්තීය පුහුණුකරුවන් සහ පුළුල් ශාරීරික සුවතා වැඩසටහන් සහිත අති නවීන ශාරීරික සුවතා මධ්‍යස්ථානය.',
                    'description_ta': 'நவீன உபகரணங்கள், தொழில்முறை பயிற்சியாளர்கள் மற்றும் விரிவான உடற்பயிற்சி திட்டங்களுடன் கூடிய அதிநவீன உடற்பயிற்சி மையம்.',
                    'operating_hours': {
                        'monday': {'open': '05:30', 'close': '22:00'},
                        'tuesday': {'open': '05:30', 'close': '22:00'},
                        'wednesday': {'open': '05:30', 'close': '22:00'},
                        'thursday': {'open': '05:30', 'close': '22:00'},
                        'friday': {'open': '05:30', 'close': '22:00'},
                        'saturday': {'open': '06:00', 'close': '21:00'},
                        'sunday': {'open': '07:00', 'close': '20:00'},
                    },
                    'amenities': ['Modern Equipment', 'Personal Trainers', 'Locker Rooms', 'Parking', 'Supplement Store', 'Cardio Zone', 'Free Weights'],
                    'status': 'approved',
                    'is_verified': True,
                    'average_rating': Decimal('4.6'),
                    'total_reviews': 78,
                    'total_bookings': 200,
                    'accepts_online_bookings': True,
                    'cancellation_policy': 'Free cancellation up to 1 hour before session time.',
                },
                'services': [
                    {
                        'name': 'Personal Training Session',
                        'name_si': 'පුද්ගලික පුහුණු සැසිය',
                        'name_ta': 'தனிப்பட்ட பயிற்சி அமர்வு',
                        'service_type': 'session',
                        'description': 'One-on-one training with certified personal trainer.',
                        'price': Decimal('3500.00'),
                        'duration_minutes': 60,
                        'max_participants': 1,
                    },
                    {
                        'name': 'Group Fitness Class',
                        'name_si': 'කණ්ඩායම් ශාරීරික සුවතා පන්තිය',
                        'name_ta': 'குழு உடற்பயிற்சி வகுப்பு',
                        'service_type': 'class',
                        'description': 'High-energy group workout sessions including HIIT, Zumba, and strength training.',
                        'price': Decimal('1200.00'),
                        'duration_minutes': 45,
                        'max_participants': 20,
                    }
                ]
            },
            {
                'user_data': {'username': 'ayurveda_kandy', 'email': 'info@ayurvedahealing.lk', 'first_name': 'Ayurveda', 'last_name': 'Healing'},
                'provider_data': {
                    'business_name': 'Traditional Ayurveda Healing Center',
                    'business_name_si': 'සම්ප්‍රදායික ආයුර්වේද සුව කිරීමේ මධ්‍යස්ථානය',
                    'business_name_ta': 'பாரம்பரிய ஆயுர்வேத சிகிச்சை மையம்',
                    'category': 'ayurveda',
                    'email': 'info@ayurvedahealing.lk',
                    'phone': '+94813456789',
                    'whatsapp': '+94813456789',
                    'address': '789 Peradeniya Road, Kandy',
                    'city': 'Kandy',
                    'district': 'kandy',
                    'postal_code': '20000',
                    'latitude': Decimal('7.2906'),
                    'longitude': Decimal('80.6337'),
                    'description': 'Authentic Ayurvedic treatments and consultations by qualified practitioners. We offer traditional therapies for holistic wellness and healing.',
                    'description_si': 'සුදුසුකම් ලත් වෛද්‍යවරුන්ගේ අව්‍යාජ ආයුර්වේද ප්‍රතිකාර සහ උපදේශන. අපි සමස්ත සුවතාව සහ සුව කිරීම සඳහා සම්ප්‍රදායික ප්‍රතිකාර ඉදිරිපත් කරමු.',
                    'description_ta': 'தகுதிவாய்ந்த பயிற்சியாளர்களால் உண்மையான ஆயுர்வேத சிகிச்சைகள் மற்றும் ஆலோசனைகள். முழுமையான நல்வாழ்வு மற்றும் குணப்படுத்துதலுக்கான பாரம்பரிய சிகிச்சைகளை நாங்கள் வழங்குகிறோம்.',
                    'operating_hours': {
                        'monday': {'open': '08:00', 'close': '18:00'},
                        'tuesday': {'open': '08:00', 'close': '18:00'},
                        'wednesday': {'open': '08:00', 'close': '18:00'},
                        'thursday': {'open': '08:00', 'close': '18:00'},
                        'friday': {'open': '08:00', 'close': '18:00'},
                        'saturday': {'open': '08:00', 'close': '16:00'},
                        'sunday': {'open': '08:00', 'close': '16:00'},
                    },
                    'amenities': ['Consultation Rooms', 'Treatment Rooms', 'Herbal Pharmacy', 'Meditation Garden', 'Parking'],
                    'status': 'approved',
                    'is_verified': True,
                    'average_rating': Decimal('4.9'),
                    'total_reviews': 67,
                    'total_bookings': 150,
                    'accepts_online_bookings': True,
                    'cancellation_policy': 'Free cancellation up to 24 hours before appointment.',
                },
                'services': [
                    {
                        'name': 'Ayurvedic Consultation',
                        'name_si': 'ආයුර්වේද උපදේශනය',
                        'name_ta': 'ஆயுர்வேத ஆலோசனை',
                        'service_type': 'consultation',
                        'description': 'Comprehensive health assessment and personalized treatment plan.',
                        'price': Decimal('2500.00'),
                        'duration_minutes': 45,
                        'max_participants': 1,
                    },
                    {
                        'name': 'Panchakarma Treatment',
                        'name_si': 'පංචකර්ම ප්‍රතිකාරය',
                        'name_ta': 'பஞ்சகர்ம சிகிச்சை',
                        'service_type': 'treatment',
                        'description': 'Complete detoxification and rejuvenation therapy.',
                        'price': Decimal('8500.00'),
                        'duration_minutes': 120,
                        'max_participants': 1,
                    }
                ]
            }
        ]

        created_count = 0
        for provider_info in sample_providers:
            try:
                # Create or get user
                user, created = User.objects.get_or_create(
                    username=provider_info['user_data']['username'],
                    defaults=provider_info['user_data']
                )
                
                if created:
                    user.set_password('samplepass123')
                    user.save()
                
                # Create provider if doesn't exist
                provider, provider_created = Provider.objects.get_or_create(
                    user=user,
                    defaults=provider_info['provider_data']
                )
                
                if provider_created:
                    # Create services
                    for service_data in provider_info['services']:
                        ProviderService.objects.create(
                            provider=provider,
                            **service_data
                        )
                    
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created provider: {provider.business_name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Provider already exists: {provider.business_name}')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating provider {provider_info["provider_data"]["business_name"]}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample providers!')
        )
        self.stdout.write('Sample providers are ready for testing the marketplace functionality.')



