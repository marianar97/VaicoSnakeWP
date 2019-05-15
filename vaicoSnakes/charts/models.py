from django.db import models
from django.conf import settings
from djongo import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class Result(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    images = ArrayField(models.CharField(max_length=10, blank=True),size=8)
    created = models.DateTimeField(auto_now_add=True)
