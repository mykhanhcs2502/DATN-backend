from rest_framework import serializers
from manager.models import Manager
from tour.models import Tour
from staff.models import Staff
from requestTour.models import AddRequest, EditRequest, CancelRequest, Request

class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Manager
        fields=('manager_ID', 'email', 'password')

class ManagerTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model=Manager
        fields=('manager_ID', 'email')

class ManagerLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model=Manager
        fields=('email', 'password')

class StaffAllSerializer(serializers.ModelSerializer):   
    # tourNum = serializers.SerializerMethodField() 
    class Meta:
        model=Staff
        fields=('staff_ID', 'email', 'phone_no', 'dateOfBirth', 'isActive', 'gender', 'lastName', 'firstName')

    # def get_tourNum(self, instance):
    #     tourlst = Tour.objects.filter(staff=instance.staff_ID)
    #     return tourlst.count()



