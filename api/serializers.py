from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import *


# Serializer for the custom user
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "first_name", "last_name", "role"]


# Serializer for university
class UniversitySerializer(serializers.ModelSerializer):
    city_name = serializers.SerializerMethodField(source="city.name", read_only=True)
    country_name = serializers.SerializerMethodField(source="country.name", read_only=True)

    def get_city_name(self, obj):
        return obj.city.name

    def get_country_name(self, obj):
        return obj.country.name
    class Meta:
        model = University
        fields = "__all__"


# Serializer for country
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"


# Serializer for city
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"


# Serializer for login
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        user = authenticate(email=email, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid credentials")
        data["user"] = user
        return data


# Serializer for registration
class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["id", "email", "password", "first_name", "last_name", "role"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


# Serializer for Google auth
class GoogleAuthSerializer(serializers.Serializer):
    token = serializers.CharField()



class MajorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Major
        fields = '__all__'


class CollageSerializer(serializers.ModelSerializer):
    major_name = serializers.SerializerMethodField(source="major.name", read_only=True)

    def get_major_name(self, obj):
        return obj.major.name
    class Meta:
        model = Collage
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField(source="user.first_name", read_only=True)

    def get_user_name(self, obj):
        return obj.user.first_name
    class Meta:
        model = Review
        fields = '__all__'


