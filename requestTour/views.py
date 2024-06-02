import random
import jwt
from rest_framework import generics
from requestTour.models import Request, EditRequest, AddRequest, CancelRequest
from tour.models import Tour, Place
from staff.models import Staff
from order_feedback.models import Order
from requestTour.serializer import *
from tour.serializer import TourUpdateSerializer, TourViewSerializer, TourSerializer
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework import views
import json
import pandas as pd
from datetime import datetime

def check_duplicate(data, typ, tour_ID, request_ID):
    if typ == "edit":
        requests_with_edits = Request.objects.filter(
                            typ="edit"
                        ).select_related(
                            'tour_ID', 'staff_ID'
                        ).prefetch_related(
                            'manager_ID', 'editrequest_set'
                        )
        request_same_tour = requests_with_edits.filter(tour_ID=tour_ID)
        if request_same_tour.count() == 0:
            return None
        
        duplicate_request = []
        for request in request_same_tour:
            edit_request = request.editrequest_set.all()[0]
            serializer = EditRequestSerializer(edit_request)
            if serializer.data == data and request.request_ID != request_ID:
                duplicate_request.append(request.request_ID)
        
        if duplicate_request == []:
            return None
        
        return duplicate_request
    
    elif typ == "add":
        requests_with_adds = Request.objects.filter(
                            typ="add"
                        ).select_related(
                            'tour_ID', 'staff_ID'
                        ).prefetch_related(
                            'manager_ID', 'addrequest_set'
                        )
        
        duplicate_request = []
        for request in requests_with_adds:
            add_request = request.addrequest_set.all()[0]
            serializer = AddRequestSerializer(add_request)
            if serializer.data == data and request.request_ID != request_ID:
                duplicate_request.append(request.request_ID)
        
        if duplicate_request == []:
            return None
        
        return duplicate_request
    
    else:
        requests_with_cancels = Request.objects.filter(
                            typ="cancel"
                        ).select_related(
                            'tour_ID', 'staff_ID'
                        ).prefetch_related(
                            'manager_ID', 'is_duplicate', 'addrequest_set'
                        ).filter(tour_ID=tour_ID)
        
        duplicate_request = []
        for request in requests_with_cancels:
            cancel_request = request.cancelrequest_set.all()[0]
            serializer = CancelRequestSerializer(cancel_request)
            if serializer.data == data and request.request_ID != request_ID:
                duplicate_request.append(request.request_ID)
        
        if duplicate_request == []:
            return None
        
        return duplicate_request

def format_errors(errors):
    error_messages = {}
    for field, messages in errors.items():
        error_messages[field] = " ".join(messages)
    return error_messages

class RequestDeleteAllAPIView(generics.DestroyAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def delete(self, request, *args, **kwargs):
        # Delete all Manager instances
        deleted_count, _ = self.get_queryset().delete()
        add_deleted_count, _ = AddRequest.objects.all().delete()
        edit_deleted_count, _ = EditRequest.objects.all().delete()
        cancel_deleted_count, _ = CancelRequest.objects.all().delete()
        return Response({'message': f'{deleted_count} Places deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

class RequestAddAllAPI(generics.CreateAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        file_request = 'requestTour/sqlScript/Request.xlsx'
        file_add_req = 'requestTour/sqlScript/Add_Request.xlsx'
        file_edit_req = 'requestTour/sqlScript/Edit_Request.xlsx'
        file_cancel_req = 'requestTour/sqlScript/Cancel_Request.xlsx'
        request = pd.read_excel(file_request)
        add_req = pd.read_excel(file_add_req)
        edit_req = pd.read_excel(file_edit_req)
        cancel_req = pd.read_excel(file_cancel_req)

        for _, row in request.iterrows():
            staffID = Staff.objects.all().order_by('?').first()
            tourID = Tour.objects.filter(tour_ID__contains=row['tourID'])
            tourID = random.choice(tourID)

            managers = list(staffID.managerID.values_list('pk', flat=True))

            request_data = {
                'request_ID': row['request_ID'],
                'status': 0,
                'staff_ID': staffID.pk,
                'reply': row['reply'],
                'typ': row['type'],
                'tour_ID': tourID.pk,
                'manager_ID': managers,
            }
            serializer = self.serializer_class(data=request_data)
            if serializer.is_valid():
                if row['type'] != "add":
                    serializer.save()

                if row['type'] == "edit":
                    tour_draft = TourUpdateSerializer(Tour.objects.get(tour_ID=tourID.pk))
                    edit_data = {
                        'request_ID': Request.objects.get(request_ID=row['request_ID']).pk,
                        'tour_draft': json.dumps(tour_draft.data, ensure_ascii=False),
                        'edit_info': json.dumps(['name'], ensure_ascii=False),
                    }
                    edit_serializer = EditRequestAddAllSerializer(data=edit_data)
                    if edit_serializer.is_valid():
                        edit_serializer.save()
                    else:
                        return Response(format_errors(edit_serializer.errors), status=status.HTTP_200_OK)
                    
                elif row['type'] == "cancel":
                    cancel_data = {
                        'request_ID': Request.objects.get(request_ID=row['request_ID']).pk,
                    }
                    cancel_serializer = CancelRequestAddAllSerializer(data=cancel_data)
                    if cancel_serializer.is_valid():
                        cancel_serializer.save()
                    else:
                        return Response(format_errors(cancel_serializer.errors), status=status.HTTP_200_OK)
            else:
                return Response(format_errors(serializer.errors), status=status.HTTP_200_OK)

        return Response({'message': 'Order created successfully'}, status=status.HTTP_201_CREATED)
    
class RequestAllAPIView(generics.ListAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        auth_header = auth_header.split(" ")[1]
        decoded_data = jwt.decode(auth_header, options={"verify_signature": False})
        manager_ID = decoded_data['data']['manager_ID']

        staff_ids = Staff.objects.filter(managerID=manager_ID).values_list('staff_ID', flat=True)

        requestlst = Request.objects.filter(staff_ID__in=staff_ids)
        request = self.serializer_class(requestlst, many=True)
        return Response(request.data, status=status.HTTP_200_OK)

class RequestGetByStaffAPIView(generics.ListAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        auth_header = auth_header.split(" ")[1]
        decoded_data = jwt.decode(auth_header, options={"verify_signature": False})
        staff_ID = decoded_data['data']['staff_ID']
        requestlst = Request.objects.filter(staff_ID=staff_ID)
        request = self.serializer_class(requestlst, many=True)
        return Response(request.data, status=status.HTTP_200_OK)
    
class RequestGetByStaffIDAPIView(generics.ListAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        staff_ID = self.request.data.get('staff_ID')
        requestlst = Request.objects.filter(staff_ID=staff_ID)
        request = self.serializer_class(requestlst, many=True)
        return Response(request.data, status=status.HTTP_200_OK)
    
class RequestGetByIDAPIView(generics.ListAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        request_ID = self.request.data.get('request_ID')
        requestlst = Request.objects.get(request_ID=request_ID)
        request = self.serializer_class(requestlst)
        result = request.data

        if requestlst == None:
            return Response(None, status=status.HTTP_200_OK)
        
        if request.data['typ'] == "edit":
            edit_req = EditRequest.objects.get(request_ID=request_ID)
            edit_serializer = EditRequestSerializer(edit_req)
            
            duplicates = check_duplicate(edit_serializer.data, "edit", requestlst.tour_ID, request_ID)
            
            tour_draft_data = json.loads(edit_req.tour_draft)
            tour_draft_serializer = TourUpdateSerializer(data=tour_draft_data)
            if tour_draft_serializer.is_valid():
                edit_info = tour_draft_serializer.data
                edit_info['schedule'] = json.loads(edit_info['schedule'].replace('\\"', '"'))
                edit_info['service'] = json.loads(edit_info['service'].replace('\\"', '"'))
                result['edit_info'] = edit_info

                tour_info = TourViewSerializer(Tour.objects.get(tour_ID=requestlst.tour_ID.pk)).data
                # tour_info['schedule'] = json.loads(tour_info['schedule'].replace('\\"', '"'))
                # tour_info['service'] = json.loads(tour_info['service'].replace('\\"', '"'))
                result['tour_info'] = tour_info

                result['edit_fields'] = json.loads(edit_serializer.data['edit_info'].replace('\\"', '"'))
                result['duplicates'] = duplicates
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(format_errors(tour_draft_serializer.errors), status=status.HTTP_200_OK)
        elif request.data['typ'] == "cancel":
            result['tour_info'] = TourViewSerializer(Tour.objects.get(tour_ID=requestlst.tour_ID.pk)).data
            cancel_req = CancelRequest.objects.get(request_ID=request_ID)
            
            cancel_serializer = CancelRequestSerializer(cancel_req)
            duplicates = check_duplicate(cancel_serializer.data, "cancel", requestlst.tour_ID, request_ID)

            result['reason'] = cancel_req.reason
            result['duplicates'] = duplicates
            return Response(result, status=status.HTTP_200_OK)
        else:
            result['add_info'] = AddRequestSerializer(AddRequest.objects.get(request_ID=requestlst.request_ID)).data

            duplicates = check_duplicate(result['add_info'], "add", None, request_ID)

            result['add_info']['schedule'] = json.loads(result['add_info']['schedule'])
            result['add_info']['service'] = json.loads(result['add_info']['service'])
            result['duplicates'] = duplicates
            return Response(result, status=status.HTTP_200_OK)
        
class RequestCreateAddAPI(generics.CreateAPIView):
    queryset = Request.objects.all()
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    
    def post(self, request, *args, **kwargs):
        # date = datetime.strptime(self.request.data.get('date'), "%m/%d/%Y, %I:%M:%S %p").date() if self.request.data.get('date') not in ["", None] else None
        # typ = self.request.data.get('type')

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({'err': 1, 'msg': 'Authorization header missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = auth_header.split(" ")[1]
            decoded_data = jwt.decode(token, options={"verify_signature": False})
            staff_ID = decoded_data['data']['staff_ID']
            staff = Staff.objects.get(staff_ID=staff_ID, isActive=True)
            manager_ID = list(staff.managerID.values_list('pk', flat=True))
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError, Staff.DoesNotExist) as e:
            return Response({'err': 1, 'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        i = 1
        while Request.objects.filter(request_ID=f"R_{i:03}").exists():
            i+=1
        request_ID = f"R_{i:03}"

        new_request = {
            'request_ID': request_ID,
            'status': 0,
            # 'date': date,
            'reply': "Chưa có",
            'typ': "add",
            'tour_ID': None,
            'staff_ID': staff.pk,
            'manager_ID': manager_ID
        }

        serializer = RequestSerializer(data=new_request)
        if serializer.is_valid():
            # request_instance = serializer.save()
            place_ids = self.request.data.get('place')
            places = Place.objects.filter(place_ID__in=place_ids) if place_ids else None

            new_add_request = {
                'name': self.request.data.get('name'),
                'departure': self.request.data.get('departure'),
                'vehicle': self.request.data.get('vehicle'),
                'seat_num': self.request.data.get('seat_num'),
                'price': self.request.data.get('price'),
                'isActive': self.request.data.get('isActive') if self.request.data.get('isActive') not in ["", None] else False,
                'starting_date':  datetime.strptime(self.request.data.get('starting_date'), "%Y_%m_%d").date(),
                'bookingDeadline': datetime.strptime(self.request.data.get('bookingDeadline'), "%Y_%m_%d").date(),
                'day_num': self.request.data.get('day_num'),
                'night_num': self.request.data.get('night_num'),
                'note': self.request.data.get('note') if self.request.data.get('note') else "No note",
                'schedule': json.dumps(self.request.data.get('schedule'), ensure_ascii=False),
                'service': json.dumps(self.request.data.get('service'), ensure_ascii=False),
                'places': [x.pk for x in places] if places is not None else None
            }

            add_req_serializer = AddRequestSerializer(data=new_add_request)
            if add_req_serializer.is_valid():
                request_instance = serializer.save()
                new_add_request['request_ID'] = request_instance.pk
                add_serializer = AddRequestAddAllSerializer(data=new_add_request)
                if add_serializer.is_valid():
                    add_serializer.save()
                # add_req_serializer.save()
                    result = add_serializer.data
                    result['schedule'] = json.loads(result['schedule'])
                    result['service'] = json.loads(result['service'])
                    return Response({'err': 0, 'msg': result}, status=status.HTTP_200_OK)
                else:
                    return Response({'err': 1, 'msg': format_errors(add_serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
            else: 
                return Response({'err': 1, 'msg': format_errors(add_req_serializer.errors)}, status=status.HTTP_200_OK)
            
        else:
            return Response({'err': 1, 'msg': format_errors(serializer.errors)}, status=status.HTTP_200_OK)
        
class RequestCreateEditAPI(generics.CreateAPIView):
    queryset = Request.objects.all()
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    
    def post(self, request, *args, **kwargs):
        tour_ID = Tour.objects.get(tour_ID=self.request.data.get('tour_ID')).pk
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({'err': 1, 'msg': 'Authorization header missing'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = auth_header.split(" ")[1]
            decoded_data = jwt.decode(token, options={"verify_signature": False})
            staff_ID = decoded_data['data']['staff_ID']
            # print(staff_ID)
            staff = Staff.objects.get(staff_ID=staff_ID, isActive=True)
            manager_ID = list(staff.managerID.values_list('pk', flat=True)) 
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError, Staff.DoesNotExist) as e:
            return Response({'err': 1, 'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        i = 1
        while Request.objects.filter(request_ID=f"R_{i:03}").exists():
            i+=1
        request_ID = f"R_{i:03}"

        new_request = {
            'request_ID': request_ID,
            'status': 0,
            'reply': "Chưa có",
            'typ': "edit",
            'tour_ID': tour_ID,
            'staff_ID': staff.pk,
            'manager_ID': manager_ID
        }

        serializer = RequestSerializer(data=new_request)
        if serializer.is_valid():
            # serializer.save()
            tour_ID = self.request.data.get('tour_ID')
            tour = Tour.objects.get(tour_ID=tour_ID)

            edit_data = self.request.data.get('edit_info')

            tour_draft = {
                'name': edit_data.get('name', tour.name),
                'departure': edit_data.get('departure', tour.departure),
                'vehicle': edit_data.get('vehicle', tour.vehicle),
                'seat_num': edit_data.get('seat_num', tour.seat_num),
                'price': edit_data.get('price', tour.price),
                'isActive': edit_data.get('isActive', tour.isActive),
                'starting_date': edit_data.get('starting_date', tour.starting_date),
                'bookingDeadline': edit_data.get('bookingDeadline', tour.bookingDeadline),
                'day_num': edit_data.get('day_num', tour.day_num),
                'night_num': edit_data.get('night_num', tour.night_num),
                'note': edit_data.get('note', tour.note),
                'schedule': json.dumps(edit_data.get('schedule'), ensure_ascii=False) if edit_data.get('schedule') else tour.schedule,
                'service': json.dumps(edit_data.get('service'), ensure_ascii=False) if edit_data.get('service') else tour.service,
            }

            tour_serializer = TourUpdateSerializer(data=tour_draft)
            if tour_serializer.is_valid():
                # print(list(self.request.data.get('edit_info', {}).keys()))
                new_edit_req = {
                    'tour_draft': json.dumps(tour_serializer.data, ensure_ascii=False),
                    'edit_info': json.dumps(list(self.request.data.get('edit_info', {}).keys()), ensure_ascii=False)
                }
                edit_serializer =  EditRequestSerializer(data=new_edit_req)
                if edit_serializer.is_valid():
                    request_instance = serializer.save()
                    new_edit_req['request_ID'] = request_instance.pk
                    add_serializer = EditRequestAddAllSerializer(data=new_edit_req)
                    if add_serializer.is_valid():
                        add_serializer.save()
                        edit_serializer.data['tour_draft'] = json.loads(edit_serializer.data['tour_draft'])
                        result = {}
                        result['tour_draft'] = json.loads(edit_serializer.data['tour_draft'])
                        result['tour_draft']['schedule'] = json.loads(result['tour_draft']['schedule'])
                        result['tour_draft']['service'] = json.loads(result['tour_draft']['service'])
                        result['edit_info'] = json.loads(edit_serializer.data['edit_info'])
                        return Response({'err': 0, 'msg': result}, status=status.HTTP_200_OK)
                    else:
                        return Response({'err': 1, 'msg': format_errors(add_serializer.errors)}, status=status.HTTP_200_OK)
                else:
                    return Response({'err': 1, 'msg': format_errors(edit_serializer.errors)}, status=status.HTTP_200_OK)
            else: 
                return Response({'err': 1, 'msg': format_errors(tour_serializer.errors)}, status=status.HTTP_200_OK)
            
        else:
            return Response({'err': 1, 'msg': format_errors(serializer.errors)}, status=status.HTTP_200_OK)
        
class RequestCreateCancelAPI(generics.CreateAPIView):
    queryset = Request.objects.all()
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    
    def post(self, request, *args, **kwargs):
        # date = datetime.strptime(self.request.data.get('date'), "%m/%d/%Y, %I:%M:%S %p").date() if self.request.data.get('date') not in ["", None] else None
        # typ = self.request.data.get('type')
        tour_ID = Tour.objects.get(tour_ID=self.request.data.get('tour_ID')).pk
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({'err': 1, 'msg': 'Authorization header missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = auth_header.split(" ")[1]
            decoded_data = jwt.decode(token, options={"verify_signature": False})
            staff_ID = decoded_data['data']['staff_ID']
            staff = Staff.objects.get(staff_ID=staff_ID, isActive=True)
            manager_ID = list(staff.managerID.values_list('pk', flat=True))
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError, Staff.DoesNotExist) as e:
            return Response({'err': 1, 'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        i = 1
        while Request.objects.filter(request_ID=f"R_{i:03}").exists():
            i+=1
        request_ID = f"R_{i:03}"

        new_request = {
            'request_ID': request_ID,
            'status': 0,
            'reply': "Chưa có",
            'typ': "cancel",
            'tour_ID': tour_ID,
            'staff_ID': staff.pk,
            'manager_ID': manager_ID
        }

        serializer = RequestSerializer(data=new_request)
        if serializer.is_valid():
            new_cancel_req = {
                'reason': self.request.data.get('reason')
            }

            cancel_serializer = CancelRequestSerializer(data=new_cancel_req)
            if cancel_serializer.is_valid():
                request_instance = serializer.save()
                new_cancel_req['request_ID'] = request_instance.pk
                add_serializer = CancelRequestAddAllSerializer(data=new_cancel_req)
                if add_serializer.is_valid():
                    add_serializer.save()
                    return Response({'err': 0, 'msg': add_serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({'err': 1, 'msg': format_errors(add_serializer.errors)}, status=status.HTTP_200_OK)
            else:
                return Response({'err': 1, 'msg': format_errors(cancel_serializer.errors)}, status=status.HTTP_200_OK)
        else:
            return Response({'err': 1, 'msg': format_errors(serializer.errors)}, status=status.HTTP_200_OK)
        
class RequestAcceptAPIView(generics.CreateAPIView):
    queryset = Request.objects.all()
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        request_ID = self.request.data.get('request_ID')
        st = self.request.data.get('status')
        reply = self.request.data.get('reply')

        tmp = Request.objects.get(request_ID=request_ID)

        if st == -1:
            tmp.status = -1
            tmp.reply = reply
            tmp.save()
            return Response({'err': 0, 'msg': reply}, status=status.HTTP_200_OK)

        if tmp.typ == "add":
            add_request = AddRequest.objects.get(request_ID=request_ID)
            
            name = add_request.name 
            same_tour = Tour.objects.filter(name=name)
            starting_date = datetime.strptime(self.request.data.get('starting_date'), "%Y_%m_%d").date() #if self.request.data.get('starting_date') != None else datetime.strptime("2024_02_28", "%Y_%m_%d").date()
            set_id = ""
            if same_tour.count() == 0:
                i = Tour.objects.count()
                while Tour.objects.filter(tour_ID=f"T_{i:03}_{starting_date}").exists():
                    i += 1
                set_id = f"T_{i:03}_{starting_date}"
            else:
                i = 0
                id = same_tour.first().tour_ID.split("_")[0]
                while Tour.objects.filter(tour_ID=f"{id}_{starting_date}_{i}").exists():
                    i += 1
                set_id = f"{id}_{starting_date}_{i}"

            tour_ID = set_id

            new_tour = {
                'tour_ID': tour_ID,
                'name': add_request.name,
                'departure': add_request.departure,
                'vehicle': add_request.vehicle,
                'seat_num': add_request.seat_num,
                'price': add_request.price,
                'isActive': add_request.isActive,
                'starting_date': add_request.starting_date,
                'bookingDeadline': add_request.bookingDeadline,
                'day_num': add_request.day_num,
                'night_num': add_request.night_num,
                'note': add_request.note,
                'schedule': add_request.schedule,
                'service': add_request.service,
                'staff': add_request.request_ID.staff_ID.pk,
                'places': add_request.places #[x.pk for x in request.places]
            }

            new_tour_serializer = TourSerializer(data=new_tour)

            if new_tour_serializer.is_valid():
                new_tour_serializer.save()
                tmp.status = 1
                tmp.reply = reply
                tmp.save()
                return Response({'err': 0, 'msg': 'success', 'data': new_tour_serializer.data}, status=status.HTTP_200_OK)
            else: 
                return Response({'err': 1, 'msg': format_errors(new_tour_serializer.errors)}, status=status.HTTP_200_OK)
        
        elif tmp.typ == "edit":
            update_request = EditRequest.objects.get(request_ID=request_ID)
            tour_draft = json.loads(update_request.tour_draft)

            serializer = TourUpdateSerializer(data=tour_draft)

            if serializer.is_valid():
                # print(update_request.request_ID.tour_ID)
                update_tour = Tour.objects.get(tour_ID=update_request.request_ID.tour_ID.pk)

                for att, value in tour_draft.items():
                    if att in update_request.edit_info:
                        setattr(update_tour, att, value)

                update_tour.save()  # Save the modified tour instance
                tmp.status = 1
                tmp.reply = reply
                tmp.save()
                return Response({'err': 0}, status=status.HTTP_200_OK)
            else:
                return Response({'err': 1, 'msg': format_errors(serializer.errors)}, status=status.HTTP_200_OK)
            
        else:
            tour = Tour.objects.get(tour_ID=tmp.tour_ID.pk)

            #xét condition
            orders = Order.objects.filter(tour_ID=tour.pk)
            for order in orders:
                order.is_cancel = True
                order.cancel_percent = 0
                order.cancel_datetime = datetime.now()
                order.save()

            tour.is_cancel = True

            tmp.status = 1
            tmp.reply = reply
            tmp.save()

            return Response({'err': 0, 'msg': "cancel success"}, status=status.HTTP_200_OK)

            

        

