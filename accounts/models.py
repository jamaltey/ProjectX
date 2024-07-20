from django.db import models
from core.models import *
from django.contrib.auth.models import AbstractUser, UnicodeUsernameValidator
from accounts.managers import UserManager

class User(AbstractUser):
    username_validator = UnicodeUsernameValidator
    username = models.CharField(
        ('username'),
        max_length=150,
        blank=True,
        null=True,
        unique=False,
        help_text=('Not Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': ("A user with that username already exists."),
        },
    )
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.EmailField(('Email Address'), unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
