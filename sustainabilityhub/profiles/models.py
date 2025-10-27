from django.db import models
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    location = models.CharField(max_length=200, blank=True)
    interests = models.JSONField(default=list, blank=True)
    skills = models.CharField(max_length=500, blank=True)


def __str__(self):
    return f'{self.user.username} profile'