from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from providers.models import Provider, ProviderService
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Create millet food providers for Sri Lankan marketplace'

    def create_user_for_provider(self, business_name):
        """Create a unique user for each provider"""
        username = business_name.lower().replace(' ', '_').replace('\'', '').replace('&', 'and')[:30]
        email = f"{username}@millets.lk"
        counter = 1
        original_username = username
        while User.objects.filter(username=username).exists():
            username = f"{original_username}_{counter}"
            counter += 1
        
        return User.objects.create(
            username=username,
            email=email,
            first_name=business_name.split()[0],
            last_name='Millets'
        )

    def handle(self, *args, **options):
        self.stdout.write('Creating millet food providers...')

        # Sri Lankan millet providers data
        millet_providers = [
            {
                'business_name': 'Rathu Kurakkan Store',
                'business_name_si': 'රතු කුරක්කන් කඩය',
                'business_name_ta': 'சிகப்பு கேழ்வரகு கடை',
                'category': 'millet_food',
                'email': 'info@rathukurakkan.lk',
                'phone': '+94112345671',
                'whatsapp': '+94771234571',
                'address': '45 Pettah Main Street, Colombo 11',
                'city': 'Colombo',
                'district': 'colombo',
                'postal_code': '01100',
                'latitude': Decimal('6.9397'),
                'longitude': Decimal('79.8542'),
                'description': 'Traditional Sri Lankan millet store specializing in finger millet (kurakkan), foxtail millet, and pearl millet. We offer organic, locally-sourced millets and millet-based products.',
                'description_si': 'සම්ප්‍රදායික ශ්‍රී ලාංකික කුරක්කන් කඩයක් ෆිංගර් මිලට් (කුරක්කන්), ෆොක්ස්ටේල් මිලට් සහ පර්ල් මිලට් විශේෂීකරණය කරයි.',
                'description_ta': 'கேழ்வரகு, தினை மற்றும் கம்பு சிறப்பு இயற்கை தானிய கடை.',
                'operating_hours': {
                    'monday': {'open': '07:00', 'close': '19:00'},
                    'tuesday': {'open': '07:00', 'close': '19:00'},
                    'wednesday': {'open': '07:00', 'close': '19:00'},
                    'thursday': {'open': '07:00', 'close': '19:00'},
                    'friday': {'open': '07:00', 'close': '19:00'},
                    'saturday': {'open': '07:00', 'close': '20:00'},
                    'sunday': {'open': '08:00', 'close': '18:00'},
                },
                'amenities': ['Organic Certified', 'Home Delivery', 'Bulk Orders', 'Custom Packaging'],
                'status': 'approved',
                'is_verified': True,
                'average_rating': Decimal('4.7'),
                'total_reviews': 89,
                'total_bookings': 45,
                'accepts_online_bookings': True,
                'cancellation_policy': 'Free cancellation up to 4 hours before delivery.',
                'services': [
                    {
                        'name': 'Organic Red Finger Millet (1kg)',
                        'name_si': 'ජෛවික රතු කුරක්කන් (කිලෝ 1)',
                        'name_ta': 'இயற்கை சிகப்பு கேழ்வரகு (1 கிலோ)',
                        'service_type': 'product',
                        'description': 'Premium quality organic red finger millet, rich in calcium and iron.',
                        'price': Decimal('450.00'),
                        'duration_minutes': 0,
                        'max_participants': 1,
                    },
                    {
                        'name': 'Kurakkan Flour (500g)',
                        'name_si': 'කුරක්කන් පිටි (ග්‍රෑම් 500)',
                        'name_ta': 'கேழ்வரகு மாவு (500 கிராம்)',
                        'service_type': 'product',
                        'description': 'Freshly ground finger millet flour for roti and traditional recipes.',
                        'price': Decimal('280.00'),
                        'duration_minutes': 0,
                        'max_participants': 1,
                    }
                ]
            },
            {
                'business_name': 'Thala Wellness Foods',
                'business_name_si': 'තල සුව ආහාර',
                'business_name_ta': 'எள் நல்வாழ்வு உணவுகள்',
                'category': 'millet_food',
                'email': 'contact@thalawellness.lk',
                'phone': '+94812345672',
                'whatsapp': '+94712345672',
                'address': '78 Dalada Veediya, Kandy',
                'city': 'Kandy',
                'district': 'kandy',
                'postal_code': '20000',
                'latitude': Decimal('7.2906'),
                'longitude': Decimal('80.6337'),
                'description': 'Health-focused millet and sesame products. We specialize in nutritious breakfast cereals, energy bars, and traditional Sri Lankan millet preparations.',
                'description_si': 'සෞඛ්‍ය අවධානය යොමු කළ කුරක්කන් සහ තල නිෂ්පාදන. අපි පෝෂ්‍ය උදෑසන ධාන්‍ය, ශක්ති දඬු සහ සම්ප්‍රදායික ශ්‍රී ලාංකික කුරක්කන් සැකසීම් විශේෂීකරණය කරමු.',
                'description_ta': 'ஆரோக்கியம் சார்ந்த தினை மற்றும் எள் பொருட்கள். ஊட்டச்சத்து காலை உணவு, எனர்ஜி பார் மற்றும் பாரம்பரிய இலங்கை தினை தயாரிப்புகள்.',
                'operating_hours': {
                    'monday': {'open': '08:00', 'close': '18:00'},
                    'tuesday': {'open': '08:00', 'close': '18:00'},
                    'wednesday': {'open': '08:00', 'close': '18:00'},
                    'thursday': {'open': '08:00', 'close': '18:00'},
                    'friday': {'open': '08:00', 'close': '18:00'},
                    'saturday': {'open': '08:00', 'close': '19:00'},
                    'sunday': {'open': '09:00', 'close': '17:00'},
                },
                'amenities': ['Nutritionist Consultation', 'Recipe Guides', 'Diet Planning', 'Online Orders'],
                'status': 'approved',
                'is_verified': True,
                'average_rating': Decimal('4.8'),
                'total_reviews': 67,
                'total_bookings': 32,
                'accepts_online_bookings': True,
                'cancellation_policy': 'Free cancellation up to 2 hours before pickup.',
                'services': [
                    {
                        'name': 'Millet Breakfast Mix',
                        'name_si': 'කුරක්කන් උදෑසන ආහාර මිශ්‍රණය',
                        'name_ta': 'தினை காலை உணவு கலவை',
                        'service_type': 'product',
                        'description': 'Nutritious breakfast cereal with mixed millets, nuts, and dried fruits.',
                        'price': Decimal('650.00'),
                        'duration_minutes': 0,
                        'max_participants': 1,
                    },
                    {
                        'name': 'Millet Energy Bars (Pack of 6)',
                        'name_si': 'කුරක්කන් ශක්ති දඬු (6ක් පැකට්)',
                        'name_ta': 'தினை எனர்ஜி பார் (6 பேக்)',
                        'service_type': 'product',
                        'description': 'Healthy energy bars made with millets, dates, and nuts.',
                        'price': Decimal('480.00'),
                        'duration_minutes': 0,
                        'max_participants': 1,
                    }
                ]
            },
            {
                'business_name': 'Gampaha Traditional Grains',
                'business_name_si': 'ගම්පහ සම්ප්‍රදායික ධාන්‍ය',
                'business_name_ta': 'கம்பஹா பாரம்பரிய தானியங்கள்',
                'category': 'millet_food',
                'email': 'info@gampahagrains.lk',
                'phone': '+94332345673',
                'whatsapp': '+94773345673',
                'address': '156 Colombo Road, Gampaha',
                'city': 'Gampaha',
                'district': 'gampaha',
                'postal_code': '11000',
                'latitude': Decimal('7.0911'),
                'longitude': Decimal('79.9966'),
                'description': 'Family-owned business specializing in traditional Sri Lankan grains including various millets. We source directly from local farmers and ensure freshness and quality.',
                'description_si': 'විවිධ කුරක්කන් ඇතුළු සම්ප්‍රදායික ශ්‍රී ලාංකික ධාන්‍ය විශේෂීකරණය කරන පවුල් ව්‍යාපාරයක්.',
                'description_ta': 'பல்வேறு தினைகள் உட்பட பாரம்பரிய இலங்கை தானியங்களில் நிபுணத்துவம் பெற்ற குடும்ப வணிகம்.',
                'operating_hours': {
                    'monday': {'open': '06:30', 'close': '19:30'},
                    'tuesday': {'open': '06:30', 'close': '19:30'},
                    'wednesday': {'open': '06:30', 'close': '19:30'},
                    'thursday': {'open': '06:30', 'close': '19:30'},
                    'friday': {'open': '06:30', 'close': '19:30'},
                    'saturday': {'open': '06:30', 'close': '20:00'},
                    'sunday': {'open': '07:00', 'close': '18:00'},
                },
                'amenities': ['Fresh Daily Stock', 'Farmer Direct', 'Quality Tested', 'Traditional Processing'],
                'status': 'approved',
                'is_verified': True,
                'average_rating': Decimal('4.6'),
                'total_reviews': 124,
                'total_bookings': 67,
                'accepts_online_bookings': True,
                'cancellation_policy': 'Free cancellation up to 6 hours before order fulfillment.',
                'services': [
                    {
                        'name': 'Mixed Millet Pack (2kg)',
                        'name_si': 'මිශ්‍ර කුරක්කන් පැකට් (කිලෝ 2)',
                        'name_ta': 'கலப்பு தினை பேக் (2 கிலோ)',
                        'service_type': 'product',
                        'description': 'Variety pack containing finger millet, foxtail millet, and pearl millet.',
                        'price': Decimal('750.00'),
                        'duration_minutes': 0,
                        'max_participants': 1,
                    },
                    {
                        'name': 'Millet Cookie Mix',
                        'name_si': 'කුරක්කන් කුකී මිශ්‍රණය',
                        'name_ta': 'தினை குக்கீ கலவை',
                        'service_type': 'product',
                        'description': 'Ready-to-bake millet cookie mix with natural sweeteners.',
                        'price': Decimal('380.00'),
                        'duration_minutes': 0,
                        'max_participants': 1,
                    }
                ]
            },
            {
                'business_name': 'Negombo Millet Hub',
                'business_name_si': 'මීගමුව කුරක්කන් මධ්‍යස්ථානය',
                'business_name_ta': 'நீர்கொழும்பு தினை மையம்',
                'category': 'millet_food',
                'email': 'hub@negombomillets.lk',
                'phone': '+94312345674',
                'whatsapp': '+94772345674',
                'address': '89 Main Street, Negombo',
                'city': 'Negombo',
                'district': 'gampaha',
                'postal_code': '11500',
                'latitude': Decimal('7.2084'),
                'longitude': Decimal('79.8380'),
                'description': 'Modern millet processing center offering a wide range of millet products and custom milling services. We cater to both retail and wholesale customers.',
                'description_si': 'මිලට් නිෂ්පාදනවල පුළුල් පරාසයක් සහ අභිරුචි ඇඹරුම් සේවා ඉදිරිපත් කරන නවීන මිලට් සැකසුම් මධ්‍යස්ථානයක්.',
                'description_ta': 'பல்வேறு தினை பொருட்கள் மற்றும் தனிப்பயன் அரைக்கும் சேவைகளை வழங்கும் நவீன தினை செயலாக்க மையம்.',
                'operating_hours': {
                    'monday': {'open': '07:00', 'close': '18:00'},
                    'tuesday': {'open': '07:00', 'close': '18:00'},
                    'wednesday': {'open': '07:00', 'close': '18:00'},
                    'thursday': {'open': '07:00', 'close': '18:00'},
                    'friday': {'open': '07:00', 'close': '18:00'},
                    'saturday': {'open': '07:00', 'close': '19:00'},
                    'sunday': {'open': '08:00', 'close': '17:00'},
                },
                'amenities': ['Custom Milling', 'Wholesale Rates', 'Quality Certification', 'Storage Facility'],
                'status': 'approved',
                'is_verified': True,
                'average_rating': Decimal('4.5'),
                'total_reviews': 98,
                'total_bookings': 54,
                'accepts_online_bookings': True,
                'cancellation_policy': 'Free cancellation up to 12 hours before custom milling appointment.',
                'services': [
                    {
                        'name': 'Custom Millet Milling Service',
                        'name_si': 'අභිරුචි කුරක්කන් ඇඹරුම් සේවාව',
                        'name_ta': 'தனிப்பயன் தினை அரைக்கும் சேவை',
                        'service_type': 'service',
                        'description': 'Fresh milling of your own millets to flour or broken grains.',
                        'price': Decimal('150.00'),
                        'duration_minutes': 30,
                        'max_participants': 1,
                    },
                    {
                        'name': 'Instant Millet Porridge Mix',
                        'name_si': 'ක්ෂණික කුරක්කන් කුඳ මිශ්‍රණය',
                        'name_ta': 'உடனடி தினை கஞ்சி கலவை',
                        'service_type': 'product',
                        'description': 'Ready-to-cook millet porridge mix with spices and vegetables.',
                        'price': Decimal('320.00'),
                        'duration_minutes': 0,
                        'max_participants': 1,
                    }
                ]
            },
            {
                'business_name': 'Matale Ancient Grains',
                'business_name_si': 'මාතලේ පුරාණ ධාන්‍ය',
                'business_name_ta': 'மாத்தளை பண்டைய தானியங்கள்',
                'category': 'millet_food',
                'email': 'grains@mataleancient.lk',
                'phone': '+94662345675',
                'whatsapp': '+94776545675',
                'address': '23 Temple Road, Matale',
                'city': 'Matale',
                'district': 'matale',
                'postal_code': '21000',
                'latitude': Decimal('7.4675'),
                'longitude': Decimal('80.6234'),
                'description': 'Specialist in ancient grains and heritage millets grown in the hills of Matale. We preserve traditional farming methods and offer rare millet varieties.',
                'description_si': 'මාතලේ කඳුකරයේ වගා කරන පුරාණ ධාන්‍ය සහ උරුම කුරක්කන් විශේෂඥයෙක්. අපි සම්ප්‍රදායික ගොවිතැන් ක්‍රම සුරකින අතර දුර්ලභ කුරක්කන් ප්‍රභේද ඉදිරිපත් කරමු.',
                'description_ta': 'மாத்தளை மலைகளில் வளர்க்கப்படும் பண்டைய தானியங்கள் மற்றும் பாரம்பரிய தினைகளில் நிபுணர்.',
                'operating_hours': {
                    'monday': {'open': '08:00', 'close': '17:00'},
                    'tuesday': {'open': '08:00', 'close': '17:00'},
                    'wednesday': {'open': '08:00', 'close': '17:00'},
                    'thursday': {'open': '08:00', 'close': '17:00'},
                    'friday': {'open': '08:00', 'close': '17:00'},
                    'saturday': {'open': '08:00', 'close': '18:00'},
                    'sunday': {'open': '09:00', 'close': '16:00'},
                },
                'amenities': ['Heritage Varieties', 'Mountain Grown', 'Traditional Methods', 'Educational Tours'],
                'status': 'approved',
                'is_verified': True,
                'average_rating': Decimal('4.9'),
                'total_reviews': 76,
                'total_bookings': 28,
                'accepts_online_bookings': True,
                'cancellation_policy': 'Free cancellation up to 24 hours before pickup.',
                'services': [
                    {
                        'name': 'Heritage Black Millet (500g)',
                        'name_si': 'උරුම කළු කුරක්කන් (ග්‍රෑම් 500)',
                        'name_ta': 'பாரம்பரிய கருப்பு தினை (500 கிராம்)',
                        'service_type': 'product',
                        'description': 'Rare heritage black millet variety grown using traditional methods.',
                        'price': Decimal('680.00'),
                        'duration_minutes': 0,
                        'max_participants': 1,
                    },
                    {
                        'name': 'Farm Visit & Millet Education Tour',
                        'name_si': 'ගොවිපල නැරඹීම සහ කුරක්කන් අධ්‍යාපන චාරිකාව',
                        'name_ta': 'பண்ணை வருகை மற்றும் தினை கல்வி சுற்றுலா',
                        'service_type': 'experience',
                        'description': 'Educational tour of heritage millet farms with traditional cooking demonstration.',
                        'price': Decimal('1500.00'),
                        'duration_minutes': 180,
                        'max_participants': 10,
                    }
                ]
            }
        ]

        created_count = 0
        for provider_data in millet_providers:
            try:
                # Extract services data
                services_data = provider_data.pop('services', [])
                
                # Create unique user
                user = self.create_user_for_provider(provider_data['business_name'])
                
                # Create provider
                provider, provider_created = Provider.objects.get_or_create(
                    business_name=provider_data['business_name'],
                    defaults={**provider_data, 'user': user}
                )
                
                if provider_created:
                    # Create services
                    for service_data in services_data:
                        ProviderService.objects.create(
                            provider=provider,
                            **service_data
                        )
                    
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Created millet provider: {provider.business_name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Millet provider already exists: {provider.business_name}')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error creating millet provider {provider_data["business_name"]}: {str(e)}')
                )

        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(f'🌾 Successfully created {created_count} millet providers!')
        )
        self.stdout.write('🇱🇰 Sri Lankan millet marketplace is ready with traditional grain providers!')

