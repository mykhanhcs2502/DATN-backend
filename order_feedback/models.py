# import json
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from customer.models import Customer
from tour.models import Tour, Place
from staff.models import Staff
from manager.models import Manager
#from django_cryptography.fields import encrypt

class Order(models.Model):
    order_ID = models.CharField(max_length=20, primary_key=True)
    pay_method = models.CharField(max_length=50, null=False)
    user_ID = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    email = models.EmailField(null=False)
    name = models.CharField(max_length=50, null=False)
    phone_no = models.CharField(max_length=10, null=False)
    date_time = models.DateTimeField(auto_now_add=True)
    note = models.TextField(null=True)
    ticket_num = models.IntegerField(null=False, default=1)
    tour_ID = models.ForeignKey(Tour, on_delete=models.SET_NULL, null=True)
    cancel_percent = models.IntegerField(default=0)
    cancel_datetime = models.DateTimeField(null=True)
    is_cancel = models.BooleanField(default=False)
    is_refund = models.BooleanField(default=False)

class Feedback(models.Model):
    feedback_ID = models.CharField(max_length=20, primary_key=True)
    ratings = models.IntegerField(
        null=False,
        validators=[
            MinValueValidator(limit_value=1),
            MaxValueValidator(limit_value=5)
        ]
    )
    reviews = models.TextField(null=True)
    datetime = models.DateTimeField(auto_now_add=True, editable=False)
    user_ID = models.ForeignKey(Customer, on_delete=models.CASCADE)
    tour_ID = models.CharField(max_length=100)
    order_ID = models.ForeignKey(Order, on_delete=models.CASCADE)