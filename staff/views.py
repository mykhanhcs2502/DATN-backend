from rest_framework import generics
from staff.models import Staff, User
from manager.models import Manager
from tour.models import Tour
from staff.serializer import *
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework import views
import pandas as pd
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.contrib.auth.hashers import make_password, check_password

class StaffTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        user = self.user
        staff_info = Staff.objects.get(email=user.username)
        serializer = StaffTokenSerializer(staff_info)
        data['info'] = serializer.data
        
        return data

class StaffLoginAPIView(TokenObtainPairView):
    queryset = Staff.objects.all()
    serializer_class = StaffLoginSerializer
    # permission_classes = [permissions.AllowAny]
    # authentication_classes = []

    def post(self, request, *args, **kwargs):
        username = self.request.data.get('username')
        password = self.request.data.get('password')

        try:
            staff = Staff.objects.get(email=username, isActive=True)
            
            if not check_password(str(password), staff.encryp_pass):
                return Response({'err': 1, 'msg': 'Mật khẩu chưa chính xác !', 'token': None})
            
            tokens = self.get_tokens_for_user(User.objects.get(username=username, is_staff=1, is_superuser=0))
            
            return Response({'err': 0, 'token': tokens['access_token'], 'refresh_token': tokens['refresh_token'], 'msg': 'Đăng nhập thành công !'}, status=status.HTTP_200_OK)
        
        except Staff.DoesNotExist:
            return Response({'err': 1, 'msg': 'Không tìm thấy người dùng !'})

    def get_tokens_for_user(self, user):
        access_token = AccessToken.for_user(user)
        refresh_token = RefreshToken.for_user(user)
        
        staff_info = Staff.objects.get(email=user.username)
        serializer = StaffTokenSerializer(staff_info)

        access_token['data'] = serializer.data
        refresh_token['data'] = serializer.data
        
        return {
            'access_token': str(access_token),
            'refresh_token': str(refresh_token),
        }

class StaffDeleteAllAPIView(generics.DestroyAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def delete(self, request, *args, **kwargs):
        # Delete all Staff instances
        deleted_count, _ = self.get_queryset().delete()
        deleted_count, _ = User.objects.filter(is_staff=1).delete()
        return Response({'message': f'{deleted_count} Staff deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

class StaffAddAllAPIView(generics.CreateAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        file_Staff = 'staff/sqlScript/Staff.xlsx'
        data = pd.read_excel(file_Staff)

        admin = Manager.objects.get(manager_ID="M_000")

        for _, row in data.iterrows():
            random_manager = Manager.objects.order_by('?').first()
            manager_ids = [random_manager.pk] + [admin.pk]

            staff_data = {
                'staff_ID': row['staff_ID'],
                'email': row['email'], 
                'phone_no': row['phone_no'], 
                'dateOfBirth': row['dateOfBirth'], 
                'isActive': True if row['isActive'] == 1 else False, 
                'gender': row['gender'], 
                'lastName': row['lastName'], 
                'firstName': row['firstName'], 
                'encryp_pass': make_password(str(row['encryp_pass'])), 
                'managerID': manager_ids
            }

            serializer = self.get_serializer(data=staff_data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_200_OK)

        return Response({'message': 'Staffs created successfully'}, status=status.HTTP_201_CREATED)
    
class StaffFirstLoginAPIView(generics.CreateAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffTokenSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        auth_header = self.request.headers.get('Authorization')
        if auth_header is None:
            return Response({'err': 1, 'msg': 'Authorization header missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        token_parts = auth_header.split(" ")
        if len(token_parts) != 2 or token_parts[0] != 'Bearer':
            return Response({'err': 1, 'msg': 'Invalid Authorization header format'}, status=status.HTTP_400_BAD_REQUEST)
        
        token = token_parts[1]
        
        try:
            decoded_data = jwt.decode(token, options={"verify_signature": False})
            staff_ID = decoded_data['data']['staff_ID']
            staff = Staff.objects.get(staff_ID=staff_ID)
            user = staff.user
            
            if decoded_data['data']['firstLogin'] is True:
                new_password = self.request.data.get('password')
                staff.encryp_pass = make_password(new_password)
                staff.firstLogin = False
                staff.save()

                user.set_password(new_password)
                user.save()
                
                return Response({'err': 0, 'msg': 'Password updated successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'err': 1, 'msg': 'Not the first login'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.DecodeError:
            return Response({'err': 1, 'msg': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except Staff.DoesNotExist:
            return Response({'err': 1, 'msg': 'Staff member not found'}, status=status.HTTP_404_NOT_FOUND)