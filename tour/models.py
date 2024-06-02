# import json
from django.db import models
from django_mysql.models import ListCharField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from staff.models import Staff

class Place(models.Model):
    place_ID = models.CharField(max_length=20, primary_key=True)
    province = models.TextField()
    description = models.TextField(default="No information")
    name = models.TextField()

class PlaceImages(models.Model):
    images = models.URLField(max_length=500, default='', blank=True, null=True)
    place_ID = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='images')

class Tour(models.Model):
    tour_ID = models.CharField(max_length=100, primary_key=True)
    name = models.TextField(max_length=1000, null=False, default='Default Tour Name')
    departure = models.CharField(max_length=100, null=False)
    vehicle = models.TextField(null=False)
    seat_num = models.IntegerField(default=0)
    tour_description = models.TextField(null=True)
    price = models.IntegerField(null=False)
    isActive = models.BooleanField(default=False)
    starting_date = models.DateField(null=False)
    bookingDeadline = models.DateField(null=False)
    day_num = models.IntegerField(null=False)
    night_num = models.IntegerField(null=False)
    note = models.TextField(null=True)
    schedule = models.TextField(default="Tour Schedule", null=False)
    service = models.TextField(default="Tour Service", null=False)
    places = models.ManyToManyField(Place)
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True)
    is_cancel = models.BooleanField(default=False)