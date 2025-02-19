from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "first_name", "last_name", "role", "is_staff")
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "role")}),
        (
            "Permissions",
            {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")},
        ),
        ("Dates", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "first_name", "last_name", "role", "is_staff", "is_active"),
        }),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Country)
admin.site.register(City)
admin.site.register(Major)
admin.site.register(Review)

class CollageInline(admin.TabularInline):  # You can also use StackedInline
    model = Collage
    extra = 1  # Number of empty collage forms shown by default

class UniversityAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    inlines = [CollageInline]  # Attach CollageInline

admin.site.register(University, UniversityAdmin)