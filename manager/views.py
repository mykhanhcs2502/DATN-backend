from datetime import datetime
import jwt
from rest_framework import generics
from manager.models import Manager, User
from staff.models import Staff
from manager.serializer import *
from staff.serializer import StaffSerializer, StaffTokenSerializer, StaffUpdateSerializer
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework import views
import pandas as pd
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from unidecode import unidecode

class ManagerDeleteAllAPIView(generics.DestroyAPIView):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def delete(self, request, *args, **kwargs):
        # Delete all Manager instances
        deleted_count, _ = self.get_queryset().delete()
        return Response({'message': f'{deleted_count} Manager deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

class ManagerAddAllAPIView(generics.CreateAPIView):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):

        admin_manager = {
            'manager_ID': "M_000", 
            'email': "admin@kbdulich.vn", 
            'password': "admin"
        }

        serializer = self.get_serializer(data=admin_manager)
        # print (serializer)
        if serializer.is_valid():
            serializer.save()
        
        file_manager = 'manager/sqlScript/manager.xlsx'
        data = pd.read_excel(file_manager)

        for _, row in data.iterrows():
            manager_data = {
                'manager_ID': row['manager_ID'], 
                'email': row['email'], 
                'password': row['password']
            }
            serializer = self.get_serializer(data=manager_data)
            print (serializer)
            if serializer.is_valid():
                serializer.save()
                print("saved")
            else:
                return Response(serializer.errors, status=status.HTTP_200_OK)

        return Response({'message': 'Managers created successfully'}, status=status.HTTP_201_CREATED)
    
class ManagerTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add additional manager information to the token
        user = self.user
        manager_info = Manager.objects.get(email=user.username)
        serializer = ManagerTokenSerializer(manager_info)
        data['info'] = serializer.data
        
        return data

class ManagerLoginAPIView(TokenObtainPairView):
    serializer_class = ManagerLoginSerializer
    # permission_classes = [permissions.AllowAny]
    # authentication_classes = []

    def post(self, request, *args, **kwargs):
        username = self.request.data.get('username')
        password = self.request.data.get('password')

        try:
            manager = Manager.objects.get(email=username)
            
            if password != manager.password:
                return Response({'err': 1, 'msg': 'Mật khẩu chưa chính xác !', 'token': None})
            
            # Generate access and refresh tokens
            tokens = self.get_tokens_for_user(User.objects.get(username=username, is_staff=0, is_superuser=1))
            
            return Response({'err': 0, 'token': tokens['access_token'], 'refresh_token': tokens['refresh_token'], 'msg': 'Đăng nhập thành công !'}, status=status.HTTP_200_OK)
        
        except Manager.DoesNotExist:
            return Response({'err': 1, 'msg': 'Không tìm thấy người dùng !'})

    def get_tokens_for_user(self, user):
        access_token = AccessToken.for_user(user)
        refresh_token = RefreshToken.for_user(user)
        
        manager_info = Manager.objects.get(email=user.username)
        serializer = ManagerTokenSerializer(manager_info)
        
        access_token['data'] = serializer.data
        refresh_token['data'] = serializer.data
        
        return {
            'access_token': str(access_token),
            'refresh_token': str(refresh_token),
        }
    
class StaffAddAPIView(generics.CreateAPIView):
    serializer_class = StaffSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        auth_header = self.request.headers.get('Authorization')
        if auth_header is None:
            return Response({'err': 1, 'msg': "No manager token"}, status=status.HTTP_200_OK)
        
        auth_header = auth_header.split(" ")[1]
        decoded_data = jwt.decode(auth_header, options={"verify_signature": False})
        manager_ID = decoded_data['data']['manager_ID']
        manager = Manager.objects.get(manager_ID=manager_ID)

        managers = [manager.pk] + [Manager.objects.get(manager_ID="M_000").pk]

        i = 1
        while Staff.objects.filter(staff_ID=f"S_{i:03}").exists():
            i+=1
        
        firstName = self.request.data.get('firstName')
        lastName = self.request.data.get('lastName').lower().replace(" ", "")
        email = f"{unidecode(firstName.lower())}.{unidecode(lastName)}@kbdulich.vn"

        if Staff.objects.filter(email=email).exists():
            j = 1
            while Staff.objects.filter(email=f"{unidecode(firstName.lower())}.{unidecode(lastName)}{j}@kbdulich.vn").exists():
                j+=1
            print(j)

            email = f"{unidecode(firstName.lower())}.{unidecode(lastName)}{j}@kbdulich.vn"

        print(email)

        new_staff = {
            'staff_ID': f"S_{i:03}",
            'email': email,
            'phone_no': self.request.data.get('phone_no'),
            'dateOfBirth': datetime.strptime(self.request.data.get('dateOfBirth'), "%Y_%m_%d").date(),
            'gender': self.request.data.get('gender'),
            'lastName': self.request.data.get('lastName'),
            'firstName': self.request.data.get('firstName'),
            'encryp_pass': f"{unidecode(firstName.lower())}.{unidecode(lastName)}",
            'managerID': managers
        }
        serializer = self.serializer_class(data=new_staff)
        if serializer.is_valid():
            serializer.save()
            return Response({'err': 0, 'msg': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'err': 1, 'msg': serializer.errors}, status=status.HTTP_200_OK)
        
class StaffAllAPIView(generics.ListAPIView):
    serializer_class = StaffAllSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        auth_header = self.request.headers.get('Authorization')
        if auth_header is None:
            return Response({'err': 1, 'msg': "No manager token"}, status=status.HTTP_200_OK)
        
        auth_header = auth_header.split(" ")[1]
        decoded_data = jwt.decode(auth_header, options={"verify_signature": False})
        manager_ID = decoded_data['data']['manager_ID']
        manager = Manager.objects.get(manager_ID=manager_ID)

        staffset = Staff.objects.filter(managerID=manager)
        
        staff = self.serializer_class(staffset, many=True)
        for i in staff.data:
            i['tour_num'] = Tour.objects.filter(staff=i['staff_ID']).count()

        return Response(staff.data, status=status.HTTP_200_OK)
    
class StaffGetByIDAPIView(generics.ListAPIView):
    serializer_class = StaffTokenSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        staff_ID = self.request.data.get('staff_ID')
        staff = Staff.objects.get(staff_ID=staff_ID)
        staff = self.serializer_class(staff).data
        # staff['tour_num'] = Tour.objects.filter(staff=staff_ID).count()
        return Response(staff, status=status.HTTP_200_OK)
    
class StaffUpdateInfoAPIView(generics.UpdateAPIView):
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
            manager_ID = decoded_data['data']['manager_ID']
            manager = Manager.objects.get(manager_ID=manager_ID)

            admin = Manager.objects.get(manager_ID="M_000")

            new_manager_ID = self.request.data.get('manager_ID') if self.request.data.get('manager_ID') else None

            managers = None
            if new_manager_ID != None: 
                new_manager = Manager.objects.get(manager_ID=new_manager_ID)
                managers = [new_manager.pk] + [admin.pk]

            staff_ID = self.request.data.get('staff_ID')
            update_staff = Staff.objects.get(pk=staff_ID)

            update_info = {
                # 'email': self.request.data.get('email') if self.request.data.get('email') else update_staff.email,
                'phone_no': self.request.data.get('phone_no') if self.request.data.get('phone_no') else update_staff.phone_no,
                'dateOfBirth': datetime.strptime(self.request.data.get('dateOfBirth'), "%Y_%m_%d").date() if self.request.data.get('dateOfBirth') else update_staff.dateOfBirth,
                # 'isActive': self.request.data.get('isActive') if self.request.data.get('isActive') else update_staff.isActive,
                'gender': self.request.data.get('gender') if self.request.data.get('gender') else update_staff.gender,
                'firstName': self.request.data.get('firstName') if self.request.data.get('firstName') else update_staff.firstName,
                'lastName': self.request.data.get('lastName') if self.request.data.get('lastName') else update_staff.lastName,
            }

            serializer = StaffUpdateSerializer(data=update_info)
            if serializer.is_valid():
                # Update staff object with new information
                for att, value in update_info.items():
                    if value is not None:
                        setattr(update_staff, att, value)
                if managers != None:
                    update_staff.managerID = managers

                    requestlst = Request.objects.filter(staff_ID=staff_ID)
                    for req in requestlst:
                        req.manager_ID = managers
                        req.save()
                        
                update_staff.save() 
                return Response({'err': 0, 'msg': 'Staff information updated successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'err': 1, 'msg': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
        except jwt.DecodeError:
            return Response({'err': 1, 'msg': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except Staff.DoesNotExist:
            return Response({'err': 1, 'msg': 'Staff member not found'}, status=status.HTTP_404_NOT_FOUND)
        
class StaffChangeActivateAPIView(generics.UpdateAPIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        staff_ID = self.request.data.get('staff_ID')
        staff = Staff.objects.get(staff_ID=staff_ID)
        staff_status = self.request.data.get('isActive')

        if staff_status == False:
            Request.objects.filter(staff_ID=staff_ID).delete()
            
            staff.isActive = False
            staff.save()

            return Response({'err': 0, 'msg': "Deactive staff successfully"}, status=status.HTTP_200_OK)
        
        staff.isActive = True
        staff.save()
        return Response({'err': 0, 'msg': "Activate staff successfully"}, status=status.HTTP_200_OK)