from django.core.management.base import BaseCommand
from nutrition.models import FoodCategory, Food, LocalFoodDatabase


class Command(BaseCommand):
    help = 'Create Sri Lankan food categories and foods'

    def handle(self, *args, **options):
        self.stdout.write('Creating Sri Lankan food categories...')
        
        # Create food categories
        categories_data = [
            {
                'name': 'Rice & Grains',
                'name_si': 'බත් සහ ධාන්‍ය',
                'name_ta': 'அரிசி மற்றும் தானியங்கள்',
                'description': 'Staple grains and rice varieties'
            },
            {
                'name': 'Vegetables',
                'name_si': 'එළවළු',
                'name_ta': 'காய்கறிகள்',
                'description': 'Fresh and local vegetables'
            },
            {
                'name': 'Fruits',
                'name_si': 'පලතුරු',
                'name_ta': 'பழங்கள்',
                'description': 'Tropical and local fruits'
            },
            {
                'name': 'Legumes & Pulses',
                'name_si': 'කොළ ගස් සහ ධාන්‍ය',
                'name_ta': 'பருப்பு வகைகள்',
                'description': 'Lentils, beans and pulses'
            },
            {
                'name': 'Spices & Herbs',
                'name_si': 'කුළුබඩු සහ ඖෂධ පැළෑටි',
                'name_ta': 'மசாலா மற்றும் மூலிகைகள்',
                'description': 'Traditional spices and herbs'
            },
            {
                'name': 'Seafood',
                'name_si': 'මුහුදු ආහාර',
                'name_ta': 'கடல் உணவு',
                'description': 'Fresh fish and seafood'
            },
            {
                'name': 'Meat & Poultry',
                'name_si': 'මස් සහ කුකුළු මස්',
                'name_ta': 'இறைச்சி மற்றும் கோழி',
                'description': 'Meat and poultry products'
            },
            {
                'name': 'Traditional Dishes',
                'name_si': 'සාම්ප්‍රදායික ආහාර',
                'name_ta': 'பாரம்பரிய உணவுகள்',
                'description': 'Traditional Sri Lankan prepared foods'
            }
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = FoodCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create Sri Lankan foods
        foods_data = [
            # Rice & Grains
            {
                'name': 'White Rice (Basmati)',
                'name_si': 'සුදු බත් (බාස්මති)',
                'name_ta': 'வெள்ளை அரிசி (பாஸ்மதி)',
                'category': 'Rice & Grains',
                'calories': 130,
                'protein_g': 2.7,
                'carbs_g': 28.0,
                'fat_g': 0.3,
                'fiber_g': 0.4,
                'origin': 'LK',
                'region': 'All',
                'common_serving_size': '1 cup cooked',
                'is_vegetarian': True,
                'is_vegan': True,
                'is_gluten_free': True,
                'description': 'Premium quality basmati rice, commonly used in Sri Lankan cuisine'
            },
            {
                'name': 'Red Rice',
                'name_si': 'රතු බත්',
                'name_ta': 'சிவப்பு அரிசி',
                'category': 'Rice & Grains',
                'calories': 216,
                'protein_g': 4.5,
                'carbs_g': 45.0,
                'fat_g': 1.8,
                'fiber_g': 3.5,
                'origin': 'LK',
                'region': 'All',
                'common_serving_size': '1 cup cooked',
                'is_vegetarian': True,
                'is_vegan': True,
                'is_gluten_free': True,
                'description': 'Nutritious red rice variety, traditional Sri Lankan staple'
            },
            # Vegetables
            {
                'name': 'Gotukola (Centella)',
                'name_si': 'ගොටුකොළ',
                'name_ta': 'வல்லாரை',
                'category': 'Vegetables',
                'calories': 20,
                'protein_g': 2.0,
                'carbs_g': 3.0,
                'fat_g': 0.2,
                'fiber_g': 1.8,
                'vitamin_c_mg': 48.5,
                'origin': 'LK',
                'region': 'All',
                'common_serving_size': '100g',
                'is_vegetarian': True,
                'is_vegan': True,
                'is_gluten_free': True,
                'description': 'Traditional medicinal leafy vegetable with brain-boosting properties'
            },
            {
                'name': 'Mukunuwenna',
                'name_si': 'මුකුණුවැන්න',
                'name_ta': 'முகுனுவென்னா',
                'category': 'Vegetables',
                'calories': 25,
                'protein_g': 2.5,
                'carbs_g': 4.0,
                'fat_g': 0.3,
                'fiber_g': 2.1,
                'vitamin_c_mg': 52.0,
                'iron_mg': 3.2,
                'origin': 'LK',
                'region': 'All',
                'common_serving_size': '100g',
                'is_vegetarian': True,
                'is_vegan': True,
                'is_gluten_free': True,
                'description': 'Nutritious green leafy vegetable, rich in vitamins and minerals'
            },
            # Fruits
            {
                'name': 'King Coconut Water',
                'name_si': 'තඹිලි වතුර',
                'name_ta': 'தென்னீர்',
                'category': 'Fruits',
                'calories': 19,
                'protein_g': 0.7,
                'carbs_g': 3.7,
                'fat_g': 0.2,
                'sodium_mg': 105,
                'origin': 'LK',
                'region': 'All',
                'common_serving_size': '240ml',
                'is_vegetarian': True,
                'is_vegan': True,
                'is_gluten_free': True,
                'description': 'Natural electrolyte drink from Sri Lankan king coconuts'
            },
            {
                'name': 'Rambutan',
                'name_si': 'රම්බුටන්',
                'name_ta': 'ரம்புட்டான்',
                'category': 'Fruits',
                'calories': 82,
                'protein_g': 0.9,
                'carbs_g': 20.9,
                'fat_g': 0.2,
                'fiber_g': 0.9,
                'vitamin_c_mg': 4.9,
                'origin': 'LK',
                'region': 'Wet Zone',
                'common_serving_size': '100g (about 5 fruits)',
                'is_vegetarian': True,
                'is_vegan': True,
                'is_gluten_free': True,
                'description': 'Sweet tropical fruit native to Sri Lanka'
            },
            # Legumes & Pulses
            {
                'name': 'Dhal (Red Lentils)',
                'name_si': 'පරිප්පු (රතු)',
                'name_ta': 'பருப்பு (சிவப்பு)',
                'category': 'Legumes & Pulses',
                'calories': 116,
                'protein_g': 9.0,
                'carbs_g': 20.1,
                'fat_g': 0.4,
                'fiber_g': 7.9,
                'iron_mg': 3.3,
                'origin': 'LK',
                'region': 'All',
                'common_serving_size': '100g cooked',
                'is_vegetarian': True,
                'is_vegan': True,
                'is_gluten_free': True,
                'description': 'Protein-rich red lentils, staple in Sri Lankan curry'
            },
            # Spices
            {
                'name': 'Ceylon Cinnamon',
                'name_si': 'කුරුඳු',
                'name_ta': 'இலவங்கம்',
                'category': 'Spices & Herbs',
                'calories': 247,
                'protein_g': 4.0,
                'carbs_g': 50.6,
                'fat_g': 1.2,
                'fiber_g': 53.1,
                'calcium_mg': 1002,
                'origin': 'LK',
                'region': 'All',
                'common_serving_size': '1 tsp ground (2g)',
                'is_vegetarian': True,
                'is_vegan': True,
                'is_gluten_free': True,
                'description': 'World-famous Ceylon cinnamon, sweet and delicate flavor'
            },
            # Seafood
            {
                'name': 'Tuna (Skipjack)',
                'name_si': 'කෙලවල්ලා',
                'name_ta': 'கெலவல்லா',
                'category': 'Seafood',
                'calories': 103,
                'protein_g': 22.0,
                'carbs_g': 0.0,
                'fat_g': 1.0,
                'origin': 'LK',
                'region': 'Coastal',
                'common_serving_size': '100g',
                'is_vegetarian': False,
                'is_vegan': False,
                'is_gluten_free': True,
                'description': 'Fresh skipjack tuna from Sri Lankan waters'
            },
            # Traditional Dishes
            {
                'name': 'Kiribath (Milk Rice)',
                'name_si': 'කිරිබත්',
                'name_ta': 'பால் சாதம்',
                'category': 'Traditional Dishes',
                'calories': 180,
                'protein_g': 4.5,
                'carbs_g': 32.0,
                'fat_g': 4.2,
                'calcium_mg': 120,
                'origin': 'LK',
                'region': 'All',
                'common_serving_size': '1 piece (150g)',
                'is_vegetarian': True,
                'is_vegan': False,
                'is_gluten_free': True,
                'description': 'Traditional Sri Lankan coconut milk rice, served on special occasions'
            }
        ]

        for food_data in foods_data:
            category = categories[food_data.pop('category')]
            food_data['category'] = category
            
            food, created = Food.objects.get_or_create(
                name=food_data['name'],
                defaults=food_data
            )
            
            if created:
                self.stdout.write(f'Created food: {food.name}')
                
                # Create LocalFoodDatabase entry for traditional foods
                if food_data.get('origin') == 'LK':
                    LocalFoodDatabase.objects.get_or_create(
                        food=food,
                        defaults={
                            'traditional_name': food.name_si or food.name,
                            'cultural_significance': f'Traditional Sri Lankan food item - {food.name}',
                            'seasonal_availability': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                            'regional_names': {'central': food.name_si, 'northern': food.name_ta},
                            'traditional_preparation': 'Prepared using traditional Sri Lankan methods',
                            'ayurvedic_properties': {'nature': 'balanced', 'taste': 'mixed', 'effect': 'nourishing'}
                        }
                    )

        self.stdout.write(self.style.SUCCESS('Successfully created Sri Lankan food database!'))
