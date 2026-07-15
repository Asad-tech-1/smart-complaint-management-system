from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "email",
        "role",
        "department",
        "is_staff",
        "is_superuser",
    )

    list_filter = (
        "role",
        "department",
        "is_staff",
        "is_superuser",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Additional Information",
            {
                "fields": (
                    "role",
                    "department",
                    "phone",
                    "profile_image",
                    "created_at",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Additional Information",
            {
                "fields": (
                    "role",
                    "department",
                    "phone",
                    "profile_image",
                )
            },
        ),
    )

    readonly_fields = (
        "created_at",
    )