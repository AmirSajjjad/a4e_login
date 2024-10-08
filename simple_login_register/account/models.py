from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.core.validators import RegexValidator


phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")

class UserManager(BaseUserManager):
    use_in_migrations = True
    
    def create_user(self, phone_number, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not phone_number:
            raise ValueError('Users must have an phone_number')
        if not password:
            raise ValueError('Users must have an password')
        
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        """
        Creates and saves a superuser with the given phone_number and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(
            phone_number,
            password=password,
            **extra_fields
        )

class User(AbstractUser):
    username = None
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        help_text='Required. 25 characters or fewer. Letters, digits, and spaces only.',
        validators=[phone_regex],
        error_messages={
            'unique': "A user with that phone_number already exists.",
        },)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phone_number