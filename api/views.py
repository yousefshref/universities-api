from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token

from .serializers import *
from .models import *

from .pagination import CustomPagination

import random

from django.core.cache import cache

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(recipient_email, subject, body, smtp_server='smtp.gmail.com', smtp_port=587):
    sender_email = 'yb2005at@gmail.com'
    sender_password = 'hjnz kzla jvka nrpm'
    try:
        # Create a MIMEText email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)
        
        # Send the email
        server.sendmail(sender_email, recipient_email, msg.as_string())
        
        # Close the server connection
        server.quit()
        
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login with email and password and return an auth token.
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": CustomUserSerializer(user).data}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(["POST"])
@permission_classes([AllowAny])
def register_verify_email(request):
    serializer = RegistrationSerializer(data=request.data)
    if CustomUser.objects.filter(email=serializer.initial_data.get("email")).exists():
        return Response({"email": ["هذا البريد الالكتروني مستخدم بالفعل"]}, status=status.HTTP_400_BAD_REQUEST)
    if serializer.is_valid():
        email = serializer.validated_data.get("email")
        # generate random 6 digit code
        code = str(random.randint(100000, 999999))
        
        # send email
        subject = "كود التحقق من حسابك"
        body = f"الكود هو {code} لا تشاركه مع احد."
        send_email(email, subject, body)

        cache.set(f"email_code_{email}", code, 60 * 60)
        
        return Response({"message": "Email verification code sent. Please enter the code."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    """
    Register a new account (student or university) and return an auth token.
    """
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data.get("email")
        code = cache.get(f"email_code_{email}")
        if str(code) != str(request.data.get("code")):
            return Response({"message": "Email verification code is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": CustomUserSerializer(user).data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


import requests

@api_view(["POST"])
@permission_classes([AllowAny])
def google_auth_view(request):
    """
    Receive a Google account token, verify it, and create or retrieve the account.
    Then return the auth token.
    """
    serializer = GoogleAuthSerializer(data=request.data)
    if serializer.is_valid():
        google_token = serializer.validated_data["token"]
        user_info = verify_google_token(google_token)
        if not user_info:
            return Response({"error": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)
        email = user_info.get("email")
        first_name = user_info.get("given_name")
        last_name = user_info.get("family_name")
        user, created = CustomUser.objects.get_or_create(
            email=email, defaults={"first_name": first_name, "last_name": last_name}
        )
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": CustomUserSerializer(user).data}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def verify_google_token(token):
    """
    Verify a Google token.
    """
    url = "https://oauth2.googleapis.com/tokeninfo"
    params = {"id_token": token}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None


# CRUD viewsets for Users, Universities, Countries, and Cities.

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication, TokenAuthentication])
def get_user(request):
    user = request.user
    serializer = CustomUserSerializer(user)
    return Response(serializer.data)

class UniversityViewSet(viewsets.ModelViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    pagination_class = CustomPagination
    # permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        # Get filter parameters from the query string
        country_param = request.query_params.get('country', '')
        city_param = request.query_params.get('city', '')
        major_param = request.query_params.get('major', '')
        page_number = request.query_params.get('page', 1)

        # Build a cache key including filters
        cache_key = (
            f"universities_list_page_{page_number}_"
            f"country_{country_param}_city_{city_param}_major_{major_param}"
        )
        # cached_data = cache.get(cache_key)
        # if cached_data:
        #     return Response(cached_data)

        queryset = self.get_queryset()

        # Apply filters based on IDs rather than names
        if country_param:
            queryset = queryset.filter(country__id=country_param)
        if city_param:
            queryset = queryset.filter(city__id=city_param)
        if major_param:
            queryset = queryset.filter(collages__major__id=major_param).distinct()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            # Group the serialized data by country and then by city
            grouped = {}
            for uni in serializer.data:
                # Adjust these keys as returned by your serializer
                country = uni.get('country_name', 'Unknown')
                city = uni.get('city_name', 'Unknown')
                if country not in grouped:
                    grouped[country] = {}
                if city not in grouped[country]:
                    grouped[country][city] = []
                grouped[country][city].append(uni)

            # Convert the grouped dictionary into the desired list structure:
            grouped_results = []
            for country, cities in grouped.items():
                cities_list = []
                for city, unis in cities.items():
                    cities_list.append({
                        "city": city,
                        "results": unis
                    })
                grouped_results.append({
                    "country": country,
                    "universities": cities_list
                })

            paginated_response = self.get_paginated_response(grouped_results)
            cache.set(cache_key, paginated_response.data, timeout=3600)  # Cache for 1 hour
            return paginated_response

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)





class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    # permission_classes = [IsAuthenticated]


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    # permission_classes = [IsAuthenticated]


class MajorViewSet(viewsets.ModelViewSet):
    queryset = Major.objects.all()
    serializer_class = MajorSerializer
    # permission_classes = [IsAuthenticated]


class CollageViewSet(viewsets.ModelViewSet):
    queryset = Collage.objects.all()  # Keep this attribute
    serializer_class = CollageSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        university_id = self.request.query_params.get('university_id')
        if university_id is not None:
            queryset = queryset.filter(university__id=university_id)
        return queryset





@api_view(["GET", "POST", "PUT", "DELETE"])
@permission_classes([AllowAny])
@authentication_classes([SessionAuthentication, TokenAuthentication])
def review_view(request, pk=None):
    if request.method == "GET":
        if pk is None:
            reviews = Review.objects.all().order_by("-id")
            if request.GET.get("collage"):
                reviews = reviews.filter(collage__id=request.GET.get("collage"))
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data)
        else:
            review = Review.objects.get(pk=pk)
            serializer = ReviewSerializer(review)
            return Response(serializer.data)

    elif request.method == "POST":
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":
        review = Review.objects.get(pk=pk)
        serializer = ReviewSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        review = Review.objects.get(pk=pk)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
