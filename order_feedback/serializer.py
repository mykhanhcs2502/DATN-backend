from rest_framework import serializers
from order_feedback.models import Order, Feedback
from customer.models import Customer
from customer.serializer import CustomerTokenSerializer

class OrderAddSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields='__all__'

class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields=('email', 'name', 'phone_no', 'note')

class OrderCancelSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields=('is_cancel', 'cancel_datetime', 'cancel_percent')

class OrderOfTourSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields='__all__'

class OrderViewSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields='__all__'

class OrderOfCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields='__all__'

class FeedbackSerializer(serializers.ModelSerializer):    
    class Meta:
        model=Feedback
        fields='__all__'

class FeedbackViewSerializer(serializers.ModelSerializer):
    customer = CustomerTokenSerializer(source='user_ID')
    
    class Meta:
        model=Feedback
        fields=('feedback_ID', 'ratings', 'reviews', 'datetime', 'tour_ID', 'customer')