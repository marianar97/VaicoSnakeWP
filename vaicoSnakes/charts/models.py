from django.db import models
from django.conf import settings

# Create your models here.

class Result(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    activities = models.CharField(blank=True, max_length=200, null = True)
    instances = models.CharField(blank=True, max_length=200, null=True)
    created = models.DateTimeField(auto_now_add=True)
