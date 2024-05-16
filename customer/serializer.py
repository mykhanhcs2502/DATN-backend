from rest_framework import serializers
from order_feedback.models import Order, Feedback
from customer.models import Customer, Customer_views_Place

class CustomerLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model=Customer
        fields=('username', 'password', 'email')

class CustomerRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model=Customer
        fields=('username', 'password', 'phone_no', 'email')

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        phone_no = data.get('phone_no')

        if Customer.objects.filter(username=username).exists():
            raise serializers.ValidationError({'err': 1, 'msg': 'Tên người dùng đã tồn tại !', 'token': None})
            
        elif Customer.objects.filter(email=email).exists():
            raise serializers.ValidationError({'err': 1, 'msg': 'Email đã được sử dụng !', 'token': None})
        
        elif Customer.objects.filter(phone_no=phone_no).exists():
            raise serializers.ValidationError({'err': 1, 'msg': 'Số điện thoại đã được sử dụng !', 'token': None})
        
        return data

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Customer
        fields=('customer_ID', 'username', 'password', 'phone_no', 'email')

class CustomerTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model=Customer
        fields=('customer_ID', 'username', 'phone_no', 'email')

class Customer_views_PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model=Customer_views_Place
        fields=('place_ID', 'user_ID')

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model=Feedback
        fields=('feedback_ID', 'ratings', 'reviews', 'datetime', 'user_ID', 'tour_ID')

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields=('order_ID', 'pay_method', 'user_ID', 'email', 'name', 'phone_no', 'date_time', 'note', 'ticket_num', 'tour_ID', 'staff_ID')

