from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


# Create a new class for CustomUserAdmin that inherits from BaseUserAdmin
class CustomUserAdmin(BaseUserAdmin): 
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "email", "pic")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "pic"),
            },
        ),
    )


# Register your CustomUser model with the CustomUserAdmin
admin.site.register(CustomUser, CustomUserAdmin)
