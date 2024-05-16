# import json
from django.db import models
from django_mysql.models import ListCharField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from manager.models import Manager
#from django_cryptography.fields import encrypt

class Staff(models.Model):
    staff_ID = models.CharField(max_length=20, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_user', null=True)
    email = models.EmailField(null=False, unique=True)
    phone_no = models.CharField(max_length=10)
    dateOfBirth = models.DateField(null=False)
    isActive = models.BooleanField(default=True)
    gender = models.CharField(max_length=3)
    lastName = models.CharField(max_length=100, null=False)
    firstName = models.CharField(max_length=100, null=False)
    encryp_pass = models.CharField(max_length=50, default="123456")
    managerID = models.ManyToManyField(Manager)
    firstLogin = models.BooleanField(default=True, null=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.user_id:
            self.user = User.objects.create_user(username=self.email, email=self.email, password=self.encryp_pass, is_staff=True)

    def delete(self, *args, **kwargs):
        # Delete associated User instance
        if self.user:
            self.user.delete()
        
        # Delete associated Token instance
        try:
            token = Token.objects.get(user=self.user)
            token.delete()
        except Token.DoesNotExist:
            pass
        
        # Call superclass delete method
        super().delete(*args, **kwargs)