from rest_framework import serializers
from staff.models import Staff
from tour.models import Tour
from requestTour.models import AddRequest, EditRequest, CancelRequest, Request

class StaffTokenSerializer(serializers.ModelSerializer):    
    class Meta:
        model=Staff
        fields=('staff_ID', 'email', 'phone_no', 'dateOfBirth', 'isActive', 'gender', 'lastName', 'firstName', 'firstLogin')
        # extra_kwargs = {'encryp_pass': {'write_only': True}}

class StaffSerializer(serializers.ModelSerializer):    
    class Meta:
        model=Staff
        fields=('staff_ID', 'email', 'phone_no', 'dateOfBirth', 'isActive', 'gender', 'lastName', 'firstName', 'encryp_pass', 'managerID')
        # extra_kwargs = {'encryp_pass': {'write_only': True}}
    
class StaffLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model=Staff
        fields=('email', 'encryp_pass')

class StaffUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Staff
        fields=('phone_no', 'dateOfBirth', 'gender', 'firstName', 'lastName')



