from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from issuer.models import Issuer


class User(AbstractUser):
    issuer = models.ForeignKey(Issuer, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return self.username
