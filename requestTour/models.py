# import json
from django.db import models
from django_mysql.models import ListCharField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from tour.models import Tour, Place
from staff.models import Staff
from manager.models import Manager
#from django_cryptography.fields import encrypt

class Request(models.Model):
    request_ID = models.CharField(max_length=20, primary_key=True)
    status = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    reply = models.CharField(max_length=200)
    typ = models.CharField(max_length=30, null=False)
    tour_ID = models.ForeignKey(Tour, null=True, on_delete=models.CASCADE)
    staff_ID = models.ForeignKey(Staff, on_delete=models.CASCADE)
    manager_ID = models.ManyToManyField(Manager)

class EditRequest(models.Model):
    tour_draft = models.TextField(default="No data", null=False)
    edit_info = models.CharField(max_length=200, null=True)
    request_ID = models.ForeignKey(Request, null=False, on_delete=models.CASCADE)
    
class AddRequest(models.Model):
    request_ID = models.ForeignKey(Request, null=False, on_delete=models.CASCADE)
    name = models.TextField(max_length=1000, null=False, default='Default Tour Name')
    departure = models.CharField(max_length=50, null=False)
    vehicle = models.TextField(null=False)
    seat_num = models.IntegerField(default=0)
    price = models.IntegerField(null=False)
    isActive = models.BooleanField(null=False)
    starting_date = models.DateField(null=False)
    bookingDeadline = models.DateField(null=False)
    day_num = models.IntegerField(null=False)
    night_num = models.IntegerField(null=False)
    note = models.CharField(max_length=100)
    schedule = models.TextField(default="Tour Schedule", null=False)
    service = models.TextField(default="Tour Service", null=False)
    places = models.ManyToManyField(Place)

class CancelRequest(models.Model):
    request_ID = models.ForeignKey(Request, null=False, on_delete=models.CASCADE)
    reason = models.TextField(default="No reason", null=False)