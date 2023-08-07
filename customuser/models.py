from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class CustomUser(AbstractUser):
    pic = models.ImageField(upload_to='', blank=True, null=True)
    about_me = models.TextField()
    favorite_food = models.CharField(max_length=255)

    def __str__(self):
        return str(self.username)
