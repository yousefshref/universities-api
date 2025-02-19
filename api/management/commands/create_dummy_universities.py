from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.models import University, Country, City
from faker import Faker
import random

CustomUser = get_user_model()

class Command(BaseCommand):
    help = 'Creates dummy data for the University model'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Ensure there are some users, countries, and cities in the database
        users = CustomUser.objects.all()
        countries = Country.objects.all()
        cities = City.objects.all()

        if not users.exists():
            self.stdout.write(self.style.ERROR('No users found. Please create some users first.'))
            return

        if not countries.exists():
            self.stdout.write(self.style.ERROR('No countries found. Please create some countries first.'))
            return

        if not cities.exists():
            self.stdout.write(self.style.ERROR('No cities found. Please create some cities first.'))
            return

        # Create 10 dummy universities
        for _ in range(10):
            university = University(
                user=random.choice(users),
                university_name=fake.company(),
                description=fake.text(),
                rating=round(random.uniform(1.0, 5.0), 2),
                collages_number=random.randint(1, 20),
                country=random.choice(countries),
                city=random.choice(cities),
                address=fake.address(),
                specific_location=fake.address(),
            )
            university.save()

        self.stdout.write(self.style.SUCCESS('Successfully created 10 dummy universities.'))