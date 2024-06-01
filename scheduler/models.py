# import json
from django.db import models

class ScheduledTask(models.Model):
    name = models.CharField(max_length=100)
    schedule = models.CharField(max_length=100)
    task_function = models.CharField(max_length=100)