from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("staff", "Staff"),
        ("user", "User"),
    )

    DEPARTMENT_CHOICES = (
        ("IT", "IT"),
        ("HR", "HR"),
        ("Facilities", "Facilities"),
        ("Finance", "Finance"),
        ("Administration", "Administration"),
        ("General", "General"),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="user"
    )

    # ✅ Make email unique
    email = models.EmailField(
        unique=True
    )

    department = models.CharField(
        max_length=30,
        choices=DEPARTMENT_CHOICES,
        default="General"
    )

    profile_image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.username