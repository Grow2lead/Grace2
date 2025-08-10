from django.core.management.base import BaseCommand
from providers.models import Provider, FitnessCenter, FitnessInstructor
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Create fitness center details for existing gym and Zumba providers'

    def handle(self, *args, **options):
        self.stdout.write('Creating fitness center details...')
        
        # Get all gym and Zumba providers that don't have fitness details
        fitness_providers = Provider.objects.filter(
            category__in=['gym', 'zumba'],
            fitness_details__isnull=True
        )
        
        created_count = 0
        
        for provider in fitness_providers:
            try:
                # Determine fitness type based on category
                fitness_type = 'gym' if provider.category == 'gym' else 'zumba'
                
                # Create fitness center details
                fitness_center = FitnessCenter.objects.create(
                    provider=provider,
                    fitness_type=fitness_type,
                    total_area_sqft=random.randint(1500, 8000),
                    max_capacity=random.randint(30, 150),
                    parking_spaces=random.randint(5, 50),
                    available_equipment=self.get_equipment_for_type(fitness_type),
                    has_air_conditioning=True,
                    has_shower_facilities=random.choice([True, False]),
                    has_locker_rooms=random.choice([True, False]),
                    has_changing_rooms=True,
                    has_parking=random.choice([True, False]),
                    has_water_station=True,
                    membership_types=['monthly', 'quarterly', 'annual'],
                    trial_class_available=True,
                    trial_class_price=Decimal('1000.00'),
                    group_classes_available=True,
                    personal_training_available=fitness_type == 'gym',
                    nutritionist_available=random.choice([True, False]) if fitness_type == 'gym' else False,
                    physiotherapist_available=random.choice([True, False]) if fitness_type == 'gym' else False,
                    min_age=16,
                    kids_programs_available=fitness_type == 'zumba',
                    senior_programs_available=True,
                    covid_safety_measures=[
                        'Temperature checks',
                        'Hand sanitizer stations',
                        'Equipment sanitization',
                        'Social distancing',
                        'Mask requirements'
                    ],
                    first_aid_certified_staff=random.choice([True, False]),
                    early_morning_access=random.choice([True, False]),
                    late_night_access=random.choice([True, False]),
                )
                
                # Create sample instructors
                self.create_instructors(fitness_center, fitness_type)
                
                created_count += 1
                self.stdout.write(f"Created fitness details for: {provider.business_name}")
                
            except Exception as e:
                self.stderr.write(f"Error creating fitness details for {provider.business_name}: {str(e)}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created fitness center details for {created_count} providers.'
            )
        )
    
    def get_equipment_for_type(self, fitness_type):
        """Get appropriate equipment based on fitness type"""
        if fitness_type == 'gym':
            return [
                'Cardio Machines',
                'Free Weights',
                'Resistance Machines',
                'Functional Training Area',
                'Kettlebells',
                'Spinning Bikes',
                'TRX Suspension',
                'Battle Ropes'
            ]
        else:  # zumba
            return [
                'Professional Sound System',
                'Mirrors',
                'Spring Floor',
                'Yoga Props',
                'Dance Equipment'
            ]
    
    def create_instructors(self, fitness_center, fitness_type):
        """Create sample instructors for the fitness center"""
        instructor_names = [
            'Kasun Perera', 'Nimali Silva', 'Roshan Fernando', 'Priya Jayawardena',
            'Saman Kumara', 'Anushka Rathnayake', 'Dilshan Mendis', 'Kavitha Dissanayake'
        ]
        
        sinhala_names = [
            'කසුන් පෙරේරා', 'නිමාලි සිල්වා', 'රොෂාන් ප්‍ෙර්නාන්දු', 'ප්‍රියා ජයවර්ධන',
            'සමන් කුමාර', 'අනුෂ්කා රත්නායක', 'දිල්ශාන් මෙන්ඩිස්', 'කවිතා දිසානායක'
        ]
        
        # Create 2-4 instructors per center
        num_instructors = random.randint(2, 4)
        selected_names = random.sample(list(zip(instructor_names, sinhala_names)), num_instructors)
        
        for i, (name, sinhala_name) in enumerate(selected_names):
            specializations = self.get_specializations_for_type(fitness_type)
            
            try:
                FitnessInstructor.objects.create(
                    fitness_center=fitness_center,
                    name=name,
                    name_si=sinhala_name,
                    specializations=random.sample(specializations, min(3, len(specializations))),
                    bio=f"Experienced {fitness_type} instructor with {random.randint(2, 15)} years of experience.",
                    certifications=[
                        'ACE Certified',
                        'ACSM Certified',
                        'Zumba Licensed' if fitness_type == 'zumba' else 'NASM Certified'
                    ],
                    years_experience=random.randint(2, 15),
                    available_days=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'],
                    hourly_rate=Decimal(str(random.randint(2000, 6000))),
                    email=f"{name.lower().replace(' ', '.')}@{fitness_center.provider.business_name.lower().replace(' ', '').replace('\'', '')}.lk",
                    phone=f"+94{random.randint(70, 77)}{random.randint(1000000, 9999999)}",
                    average_rating=Decimal(str(round(random.uniform(4.0, 5.0), 1))),
                    total_reviews=random.randint(10, 100),
                )
            except Exception as e:
                self.stderr.write(f"Error creating instructor {name}: {str(e)}")
    
    def get_specializations_for_type(self, fitness_type):
        """Get appropriate specializations based on fitness type"""
        if fitness_type == 'gym':
            return [
                'personal_training',
                'group_fitness',
                'strength_training',
                'cardio',
                'nutrition'
            ]
        else:  # zumba
            return [
                'zumba',
                'dance',
                'aerobics',
                'group_fitness'
            ]



