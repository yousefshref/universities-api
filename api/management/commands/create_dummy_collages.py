from django.core.management.base import BaseCommand
from api.models import Collage, University, Major
from faker import Faker
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Creates dummy data for the Collage model'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Ensure there are some universities in the database
        universities = University.objects.all()
        majors = Major.objects.all()

        if not universities.exists():
            self.stdout.write(self.style.ERROR('No universities found. Please create some universities first.'))
            return

        # Create 20 dummy collages
        for _ in range(20):
            university = random.choice(universities)
            established_date = fake.date_between(start_date='-50y', end_date='today')

            collage = Collage(
                university=university,
                collage_name=f"{fake.company()} College",
                major=random.choice(majors),
                students_count=random.randint(100, 5000),
                established_date=established_date,
                accreditation=fake.random_element(elements=("AAA", "AAB", "AAC", "ABA", "ABB")),
                website=fake.url(),
                description=fake.text(),
                address=fake.address(),
                ranking=random.randint(1, 100) if random.choice([True, False]) else None,
            )
            collage.save()

        self.stdout.write(self.style.SUCCESS('Successfully created 20 dummy collages.'))