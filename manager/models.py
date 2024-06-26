from django.db import models
from django_mysql.models import ListCharField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class Manager(models.Model):
    manager_ID = models.CharField(max_length=20, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='manager_user', null=True)
    email = models.EmailField(null=False, unique=True)
    password = models.TextField(null=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.user_id:
            self.user = User.objects.create_user(username=self.email, email=self.email, password=self.password, is_superuser=True)

    def delete(self, *args, **kwargs):
        
        if self.user:
            self.user.delete()
        
        try:
            token = Token.objects.get(user=self.user)
            token.delete()
        except Token.DoesNotExist:
            pass
        
        # Call superclass delete method
        super().delete(*args, **kwargs)
