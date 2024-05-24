from rest_framework import serializers
from requestTour.models import Request, AddRequest, CancelRequest, EditRequest
import json

class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model=Request
        fields='__all__'

class AddRequestAddAllSerializer(serializers.ModelSerializer):
    class Meta:
        model=AddRequest
        fields='__all__'

class AddRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model=AddRequest
        fields=('name', 'departure', 'vehicle', 'seat_num', 'price', 'isActive', 'starting_date', 'bookingDeadline', 'day_num', 'night_num', 'note', 'schedule', 'service', 'places')

class EditRequestAddAllSerializer(serializers.ModelSerializer):
    class Meta:
        model=EditRequest
        fields='__all__'

class EditRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model=EditRequest
        fields=('tour_draft', 'edit_info')

class CancelRequestAddAllSerializer(serializers.ModelSerializer):
    class Meta:
        model=CancelRequest
        fields='__all__'

class CancelRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model=CancelRequest
        fields=('reason', )