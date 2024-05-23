# import json
from django.db import models
from tour.models import Place
from django_mysql.models import ListCharField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
#from django_cryptography.fields import encrypt

class Customer(models.Model):
    customer_ID = models.CharField(max_length=20, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_user', null=True)
    username = models.CharField(max_length=50, null=False, unique=True)
    password = models.CharField(max_length=50, null=False)
    phone_no = models.CharField(max_length=10, null=False, unique=True)
    email = models.EmailField(max_length=50, null=False, unique=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if not self.user_id:
            self.user = User.objects.create_user(username=self.email, email=self.email, password=self.password)
            
            # permissions = Permission.objects.filter(codename__in=['add_feedback', 'view_tour', 'view_user', 'view_customer'])
            # for permission in permissions:
            #     self.user.user_permissions.add(permission)


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
    
    def __str__(self):
        return self.customer_ID
    
class Profile(models.Model):
    """user = models.OneToOneField(Customer , on_delete=models.CASCADE)"""
    email = models.EmailField(max_length=50, null=False, default='', unique=True)
    forget_password_token = models.CharField(max_length=100, null=True)

class Customer_views_Place(models.Model):
    place_ID = models.ForeignKey(Place, on_delete=models.CASCADE)
    user_ID = models.ForeignKey(Customer, on_delete=models.CASCADE)