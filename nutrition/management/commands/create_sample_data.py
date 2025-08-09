from django.core.management.base import BaseCommand
from nutrition.models import Food
from users.models import User
from datetime import date


class Command(BaseCommand):
    help = 'Create sample food data for testing'

    def handle(self, *args, **options):
        # Create sample foods
        foods_data = [
            {
                'name': 'Rice',
                'localized_name_si': 'හාල්',
                'localized_name_ta': 'அரிசி',
                'serving_size_grams': 100,
                'calories': 130,
                'protein_g': 2.7,
                'carbs_g': 28,
                'fat_g': 0.3,
            },
            {
                'name': 'Chicken Breast',
                'localized_name_si': 'කුකුල් මස්',
                'localized_name_ta': 'கோழி மார்பு',
                'serving_size_grams': 100,
                'calories': 165,
                'protein_g': 31,
                'carbs_g': 0,
                'fat_g': 3.6,
            },
            {
                'name': 'Eggs',
                'localized_name_si': 'බිත්තර',
                'localized_name_ta': 'முட்டைகள்',
                'serving_size_grams': 50,
                'calories': 78,
                'protein_g': 6.3,
                'carbs_g': 0.6,
                'fat_g': 5.3,
            },
            {
                'name': 'Banana',
                'localized_name_si': 'කෙසෙල්',
                'localized_name_ta': 'வாழைப்பழம்',
                'serving_size_grams': 118,
                'calories': 105,
                'protein_g': 1.3,
                'carbs_g': 27,
                'fat_g': 0.4,
            },
            {
                'name': 'Milk',
                'localized_name_si': 'කිරි',
                'localized_name_ta': 'பால்',
                'serving_size_grams': 244,
                'calories': 103,
                'protein_g': 8,
                'carbs_g': 12,
                'fat_g': 2.4,
            },
        ]

        for food_data in foods_data:
            food, created = Food.objects.get_or_create(
                name=food_data['name'],
                defaults=food_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created food: {food.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Food already exists: {food.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Sample food data created successfully!')
        )
