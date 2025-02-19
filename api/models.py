from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, first_name="", last_name="", role="student", **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, first_name="", last_name="", role="admin", **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, first_name, last_name, role, **extra_fields)


# Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    role = models.CharField(
        max_length=20,
        choices=[("student", "Student"), ("university", "University")],
        default="student",
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Email & password are required by default

    def __str__(self):
        return self.email


# Country Model
class Country(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# City Model (Country is the parent)
class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="cities")

    def __str__(self):
        return f"{self.name}, {self.country.name}"


# University Model
class University(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="universities")
    university_name = models.CharField(max_length=255)
    image = models.TextField(null=True, blank=True)
    description = models.TextField(blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    collages_number = models.IntegerField(default=0)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name="universities")
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, related_name="universities")
    address = models.CharField(max_length=255, blank=True)
    specific_location = models.CharField(max_length=255, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.university_name
    

class Major(models.Model):
    name = models.CharField(max_length=255)
    image = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Collage(models.Model):
    """
    Represents a collage (college) within a university.
    """
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name="collages")
    collage_name = models.CharField(max_length=255)
    image = models.TextField(blank=True)
    major = models.ForeignKey(Major, on_delete=models.SET_NULL, null=True, related_name="collages")
    students_count = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.collage_name




class Review(models.Model):
    """
    Review model for students to review colleges.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="reviews", null=True, blank=True)
    collage = models.ForeignKey(Collage, on_delete=models.CASCADE, related_name="reviews")
    text = models.TextField()
    rating = models.CharField(max_length=10, choices=[("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5")])
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name}'s review on {self.collage.collage_name}"





from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg


@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def update_university_rating(sender, instance, **kwargs):
    """
    Updates the university rating whenever a review is created or deleted.
    """
    university = instance.collage.university
    avg_rating = Review.objects.filter(collage__university=university).aggregate(Avg('rating'))['rating__avg']
    
    if avg_rating is None:
        avg_rating = 0.0  # If no reviews exist, set rating to 0
    
    university.rating = round(avg_rating, 2)
    university.save()

