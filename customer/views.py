from tokenize import TokenError
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
import jwt
from rest_framework import generics
from customer.models import Customer
from manager.serializer import ManagerTokenSerializer
from staff.models import Staff, Manager
from customer.serializer import *
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import status
from rest_framework import views
from rest_framework import permissions
import pandas as pd
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from customer.models import Profile
from customer.helpers import send_forget_password_mail
import uuid

from staff.serializer import StaffTokenSerializer

class CustomerTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add additional customer information to the token
        user = self.user
        customer_info = Customer.objects.get(email=user.username)
        serializer = CustomerTokenSerializer(customer_info)
        data['info'] = serializer.data
        
        return data

class CustomerLoginAPIView(TokenObtainPairView):
    serializer_class = CustomerLoginSerializer
    queryset = Customer.objects.all()
    # permission_classes = [permissions.AllowAny]
    # authentication_classes = []

    def post(self, request, *args, **kwargs):
        username = self.request.data.get('username')
        password = self.request.data.get('password')

        try:
            customer = Customer.objects.get(email=username)
            
            if not check_password(password, customer.password):
                return Response({'err': 1, 'msg': 'Mật khẩu chưa chính xác !', 'token': None})
            
            # Generate access and refresh tokens
            tokens = self.get_tokens_for_user(User.objects.get(username=username, is_staff=0, is_superuser=0))
            
            return Response({'err': 0, 'token': tokens['access_token'], 'refresh_token': tokens['refresh_token'], 'msg': 'Đăng nhập thành công !'}, status=status.HTTP_200_OK)
        
        except Customer.DoesNotExist:
            return Response({'err': 1, 'msg': 'Không tìm thấy người dùng !'})

    def get_tokens_for_user(self, user):
        access_token = AccessToken.for_user(user)
        refresh_token = RefreshToken.for_user(user)
        
        customer_info = Customer.objects.get(email=user.username)
        serializer = CustomerTokenSerializer(customer_info)

        access_token['data'] = serializer.data
        refresh_token['data'] = serializer.data
        
        return {
            'access_token': str(access_token),
            'refresh_token': str(refresh_token),
        }

class CustomerDeleteAllAPIView(generics.DestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def delete(self, request, *args, **kwargs):
        # Delete all Customer instances
        deleted_count, _ = self.get_queryset().delete()
        deleted_count, _ = User.objects.filter(is_staff=0, is_superuser=0).delete()
        deleted_count, _ = Profile.objects.all().delete()
        return Response({'message': f'{deleted_count} customers deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

class CustomerAddAllAPIView(generics.CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        file_customer = 'customer/sqlScript/Customer.xlsx'
        data = pd.read_excel(file_customer)

        for _, row in data.iterrows():
            customer_data = {
                'customer_ID': row['user_ID'],
                'username': row['username'],
                'password': make_password(str(row['password'])),
                'phone_no': row['phone_no'],
                'email': row['email']
            }
            # print(customer_data)
            serializer = self.get_serializer(data=customer_data)
            
            if serializer.is_valid():
                serializer.save()
            else:
                print(serializer.errors)

        return Response({'message': 'Customers created successfully'}, status=status.HTTP_201_CREATED)
    
class CustomerCreate(generics.CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerRegisterSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            username = self.request.data.get('username')
            phone_no = self.request.data.get('phone_no')
            email = self.request.data.get('email')

            i = 1
            while Customer.objects.filter(customer_ID=f"U_{i}").exists():
                i += 1

            customer_id = f"U_{i}"

            new_customer = Customer.objects.create(
                customer_ID = customer_id,
                username = username,
                password = make_password(str(request.data['password'])),
                phone_no = phone_no,
                email    = email
            )

            profile_obj = Profile.objects.create(email = email)
            profile_obj.save()

            serializer = CustomerTokenSerializer(new_customer)
            response_data = {'err': 0, 'msg': 'success', 'token': serializer.data}
            return Response(response_data, status=status.HTTP_201_CREATED)
                
            
        else:
            errors = serializer.errors
            error = 0
            # tmp = []
            if 'username' in errors:
                error = error + 1
                # tmp.append('Tên người dùng đã tồn tại !')
                return Response({'error': error, 'msg': 'Tên người dùng đã tồn tại !', 'token': None}, status=status.HTTP_200_OK)
            if 'email' in errors:
                error = error + 1
                # tmp.append('Email đã được sử dụng !')
                return Response({'error': error, 'msg': 'Email đã được sử dụng !', 'token': None}, status=status.HTTP_200_OK)
            if 'phone_no' in errors:
                error = error + 1
                # tmp.append('Số điện thoại đã được sử dụng !')
                return Response({'error': error, 'msg': 'Số điện thoại đã được sử dụng !', 'token': None}, status=status.HTTP_200_OK)

class ForgetPassword(views.APIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerLoginSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        username = self.request.data.get('email')

        try:
            customer = Customer.objects.get(email=username) #Lấy ra nguyên 1 cái object của Customer nếu thỏa điều kiện trong ()
            
            serializer = self.serializer_class(customer)
            token = str(uuid.uuid4())
            profile_obj = Profile.objects.get(email = customer.email)
            profile_obj.forget_password_token = token
            profile_obj.save()
            send_forget_password_mail(customer.email, token)
            return Response({'err': 0, 'msg': 'Vui lòng kiểm tra email và nhấn vào đường link để thay đổi password !'}, status=status.HTTP_200_OK)
        
        except Customer.DoesNotExist:
            return Response({'err': 1, 'msg': 'Không tìm thấy người dùng !'})
        
class ChangePassword(views.APIView):
    queryset = Profile.objects.all()
    serializer_class = CustomerLoginSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        new_password = self.request.data.get('new_password')
        confirm_new_password = self.request.data.get('confirm_new_password')
        token = self.request.data.get('email_token')

        try:
            profile_obj = Profile.objects.get(forget_password_token = token)
            if new_password != confirm_new_password:
                return Response({'err': 1, 'msg': 'Mật khẩu nhập lại không trùng khớp !'})
            
            #serializer = self.serializer_class(customer)
            #user_obj = customer
            #token = str(uuid.uuid4())
            #send_forget_password_mail(customer.email, token)
            
            customer = Customer.objects.get(email = profile_obj.email)
            customer.password = new_password
            customer.save()
            serializer = self.serializer_class(customer)
            return Response({'err': 0, 'msg': 'Đổi mật khẩu thành công !'}, status=status.HTTP_200_OK)
        
        except Profile.DoesNotExist:
            return Response({'err': 1, 'msg': 'Không tìm thấy !'})

class GetCurrentAPI(views.APIView):
    # serializer_class = CustomerTokenSerializer
    queryset = Customer.objects.all()
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        # auth_header = request.headers.get('Authorization')
        auth_header = self.request.headers.get('Authorization').split(" ")[1]

        decoded_data = jwt.decode(auth_header, options={"verify_signature": False})
        data = decoded_data.get('data', {})

        return Response(data, status=status.HTTP_200_OK)

class AuthRefreshTokenAPI(views.APIView):
    # serializer_class = CustomerTokenSerializer
    queryset = Customer.objects.all()
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        # auth_header = request.headers.get('Authorization')
        auth_header = self.request.data.get('refresh_token')
        role = self.request.data.get('role')
        
        if auth_header:
            try:
                refresh_token = auth_header.split(" ")[1]
                refreshed_token = RefreshToken(refresh_token)

                try:
                    refreshed_token.verify()
                except TokenError as e:
                    return Response({'err': 1, 'msg': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

                decoded_data = jwt.decode(refresh_token, options={"verify_signature": False})
                email = decoded_data['data']['email']
                user = User.objects.get(username=email)

                new_refresh_token = RefreshToken.for_user(user)

                serializer = None
                if role == "customer":
                    customer_info = Customer.objects.get(email=user.username)
                    serializer = CustomerTokenSerializer(customer_info)
                elif role == "staff":
                    staff_info = Staff.objects.get(email=user.username)
                    serializer = StaffTokenSerializer(staff_info)
                else: 
                    manager_info = Manager.objects.get(email=user.username)
                    serializer = ManagerTokenSerializer(manager_info)

                new_refresh_token['data'] = serializer.data

                new_access_token = str(RefreshToken(str(new_refresh_token)).access_token)

                return Response({'err': 0, 'token': str(new_access_token), 'refresh_token': str(new_refresh_token)}, status=status.HTTP_200_OK)
            
            except IndexError:
                return Response({'err': 1, 'msg': 'Invalid authorization header format'}, status=status.HTTP_200_OK)
            
            except Exception as e:
                return Response({'err': 1, 'msg': str(e)}, status=status.HTTP_200_OK)
        
        else:
            return Response({'err': 1, 'msg': 'Authorization header not provided'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def hello_world(request):
    return Response({'message': 'Hello, world!'})





