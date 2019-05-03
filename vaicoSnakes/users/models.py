from django.db import models
from django.contrib.auth.models import User 

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business = models.CharField(blank=True,max_length=50, null = True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    picture = models.ImageField(
        upload_to="static/img/profile_pics", 
        blank=True,
        null=True
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username