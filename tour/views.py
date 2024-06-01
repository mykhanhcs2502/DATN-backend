from django.db.models.functions import TruncMonth, TruncQuarter
import calendar
from datetime import datetime, timedelta
import json
from django.db.models import Q, Avg, Sum
import jwt
from rest_framework import generics
from staff.models import Staff
from tour.models import Tour, Place
from order_feedback.models import Feedback
from requestTour.models import Request, AddRequest, CancelRequest, EditRequest
from tour.serializer import *
from order_feedback.serializer import *
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import status
from rest_framework import views
from django.db.models import Count, F, Case, When, IntegerField, Value
from rest_framework import permissions
import pandas as pd

class PlaceDeleteAllAPIView(generics.DestroyAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def delete(self, request, *args, **kwargs):
        # Delete all Manager instances
        deleted_count, _ = self.get_queryset().delete()
        return Response({'message': f'{deleted_count} Places deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
class TourDeleteAllAPIView(generics.DestroyAPIView):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def delete(self, request, *args, **kwargs):
        # Delete all Manager instances
        deleted_count, _ = self.get_queryset().delete()
        return Response({'message': f'{deleted_count} Tour deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

class PlaceAddAllAPIView(generics.CreateAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        file_place = 'tour/sqlScript/Places.xlsx'
        data = pd.read_excel(file_place)

        try:
            for _, row in data.iterrows():
                place_data = {
                    'place_ID': row['place_ID'],
                    'province': row['province'],
                    'description': row['description'],
                    'name': row['name']
                }
                
                serializer = self.get_serializer(data=place_data)
                serializer.is_valid(raise_exception=True)  # Validate data, raise exception if invalid
                serializer.save()
            return Response({'message': 'Places created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': f'Error creating places: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PlaceAllAPIView(generics.ListAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceAndImageSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        placelst = self.get_serializer(Place.objects.all(), many=True)
        return Response(placelst.data, status=status.HTTP_200_OK)
    
class PlaceGetAllConditionAPIView(generics.ListAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceAndImageSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        place_ID = None if self.request.data.get('id') in ["", None] else self.request.data.get('id')
        name = None if self.request.data.get('name') in ["", None] else self.request.data.get('name')
        province = None if self.request.data.get('province') in ["", None] else self.request.data.get('province')

        cond = []
        if place_ID != None:
            cond.append(Q(**{'place_ID': place_ID}))
        if name != None:
            cond.append(Q(**{'name__icontains': name}))
        if province != None:
            cond.append(Q(**{'province__icontains': province}))

        place_set = Place.objects.all()
        placelst = place_set.filter(*cond)
        place_lst = self.serializer_class(placelst, many=True)
        result = {'err': 0, 'count': placelst.count(), 'row': place_lst.data}

        return Response(result, status=status.HTTP_200_OK)

class PlaceImagesAddAllAPIView(generics.CreateAPIView):
    queryset = PlaceImages.objects.all()
    serializer_class = PlaceImagesAddSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        file_path = 'tour/sqlScript/PlaceImages.xlsx'
        data = pd.read_excel(file_path)

        for _, row in data.iterrows():
            place_ID = Place.objects.get(place_ID=row['place_ID'])
            image = {
                'images': row['images'],
                'place_ID': place_ID.pk
            }

            serializer = self.get_serializer(data=image)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_200_OK)
        
        return Response({"Place Images add successfully"}, status=status.HTTP_201_CREATED)

class PlaceSearchByName(generics.ListAPIView):
    place_set = Place.objects.all()
    place_serializer = PlaceAndImageSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        name = self.request.data.get('name', None)

        places = Place.objects.filter(name__icontains=name)

        if places.exists():
            serializer = self.get_serializer(places, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Place not found."}, status=status.HTTP_404_NOT_FOUND)

class ToursGetAllConditionAPIView(generics.ListAPIView):
    queryset = Tour.objects.all()
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    serializer_class = TourViewByCondSerializer

    def post(self, request, *args, **kwargs):        
        condition = {'day_num': None, 'departure': None, 'isActive': None,
                     'starting_date': None, 'destination': None, 'price': None, 'seat_num': None,
                     'vehicle': None, 'ticket_num': None}
        
        # page = None if self.request.data.get('page') == "null" else int(self.request.data.get('page'))
        # limit = int(self.request.data.get('limit'))
        condition['day_num'] = None if self.request.data.get('day_num') in ["", None] else self.request.data.get('day_num')
        condition['departure'] = None if self.request.data.get('departure') in ["", None] else self.request.data.get('departure')
        condition['starting_date'] = None if self.request.data.get('starting_date') in ["", None] else datetime.strptime(self.request.data.get('starting_date'), "%Y_%m_%d").date()
        condition['destination'] = None if self.request.data.get('destination') in ["", None] else self.request.data.get('destination')
        condition['price'] = None if self.request.data.get('price') in ["", None] else self.request.data.get('price')
        condition['seat_num'] = None if self.request.data.get('seat_num') in ["", None] else self.request.data.get('seat_num')
        condition['vehicle'] = None if self.request.data.get('vehicle') in ["", None] else self.request.data.get('vehicle')
        condition['isActive'] = None if self.request.data.get('isActive') in ["", None] else int(self.request.data.get('isActive'))
        condition['ticket_num'] = None if self.request.data.get('ticket_num') in ["", None] else self.request.data.get('ticket_num')

        tour_set = Tour.objects.all()
        if condition['ticket_num'] != None:
            tour_set = Tour.objects.annotate(
                # ticket_num=Case(
                #     When(seat_num__isnull=False, then=F('seat_num') - Count('order')),
                #     default=Value(None),
                #     output_field=IntegerField()
                # )
                total_ticket_num=Sum('order__ticket_num'), # calculate the sum of occupied ticket_num
                ticket_num=Case(
                    When(seat_num__isnull=False, then=F('seat_num') - F('total_ticket_num')), # get the remaining ticket_num
                    default=Value(None),
                    output_field=IntegerField()
                )
            )
            # print(tour_set[2].tour_ID, tour_set[2].ticket_num)

        cond = []
        for key, value in condition.items():
            if value != None:
                if key in ['price', 'day_num', 'seat_num', 'ticket_num']:
                    if value[0] == 'E':
                        cond.append(Q(**{key: int(value[1:])}))
                    elif value[0] == 'A':
                        cond.append(Q(**{key + '__gte': int(value[1:])}))
                    elif value[0] == 'U':
                        cond.append(Q(**{key + '__lte': int(value[1:])}))
                    else:
                        i1 = value.index('T')
                        i2 = i1 + 1
                        cond.append(Q(**{key + '__gte': int(value[1:i1])}))
                        cond.append(Q(**{key + '__lte': int(value[i2:])}))
                elif key == "vehicle":
                    value = value.split(",")
                    for vehicle in value:
                        if vehicle == "bus":
                            cond.append(Q(**{key + '__icontains': "Xe khách"}))
                        elif vehicle == "car":
                            cond.append(Q(**{key + '__icontains': "chỗ"}))
                        else:
                            cond.append(Q(**{key + '__icontains': "Máy bay"}))
                elif type(value) is not str and key != 'isActive':
                    cond.append(Q(**{key + '__gte': value}))
                elif key == 'destination':
                    cond.append(Q(**{'places__province__icontains': value}))
                else:
                    cond.append(Q(**{key: value}))

        # print(cond)
        cond.append(Q(**{'is_cancel': False}))
        cond.append(Q(**{'isActive': True}))

        tour_queryset = tour_set.filter(*cond).order_by('starting_date')
        # print(tour_queryset)
        number = tour_queryset.count()
        tour_list = self.serializer_class(tour_queryset, many=True)
        
        result = {'count': number, 'row': tour_list.data}
        return Response(result, status=status.HTTP_200_OK)
    
    # def get_permissions(self):
    #     if self.request.method == 'POST':
    #         # Allow POST requests without authentication
    #         return [AllowAny]
    #     else:
    #         # Use the default permission classes for other methods
    #         return super().get_permissions()

class TourGetByNameAPIView(generics.ListAPIView):
    queryset = Tour.objects.all()
    serializer_class = PlaceTourSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        name = self.request.data.get('name')
        tour = Tour.objects.filter(name__icontains=name, is_cancel=False)
        tour_list = self.serializer_class(tour, many=True)
        result = {'count': tour.count(), 'row': tour_list.data}
        return Response(result, status=status.HTTP_200_OK)

class TourAddAllAPIView(generics.CreateAPIView):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        file_tour = 'tour/sqlScript/Tour.xlsx'
        file_tour_place = 'tour/sqlScript/Tour_has_Place.xlsx'
        file_tour_schedule = 'tour/sqlScript/TourSchedule.xlsx'
        file_tour_service = 'tour/sqlScript/TourService.xlsx'
        data_tour = pd.read_excel(file_tour)
        data_tour_place = pd.read_excel(file_tour_place)
        date_tour_schedule = pd.read_excel(file_tour_schedule)
        data_tour_service = pd.read_excel(file_tour_service)

        try:
            for _, row in data_tour.iterrows():
                tour_id = f"{row['tour_id']}_{row['starting_date']}"
                if Tour.objects.filter(tour_ID=tour_id).exists():
                    i = 1
                    while Tour.objects.filter(tour_ID=f"{tour_id}_{i}").exists():
                        i += 1
                    tour_id = f"{tour_id}_{i}"

                schedule = date_tour_schedule[date_tour_schedule['tour_id'] == row['tour_id']]
                schedule = schedule['Tschedule']
                schedule_data = schedule.to_json(force_ascii=False, orient='values')

                # schedule_data_list = json.loads(schedule_data)
                # first_item = schedule_data_list[0]
                # print(first_item)

                service = data_tour_service[data_tour_service['tour_id'] == row['tour_id']]
                service = service['Tservice']
                service_data = service.to_json(force_ascii=False, orient='values')

                place_ids = data_tour_place.loc[data_tour_place['tour_id'] == row['tour_id'], 'place_ID'].tolist()

                places = Place.objects.filter(place_ID__in=place_ids)
                random_staff = Staff.objects.order_by('?').first()

                tour_data = {
                    'tour_ID': tour_id,                        
                    'name': row['name'],
                    'departure': row['departure'],
                    'vehicle': row['vehicle'],
                    'seat_num': row['seatNum'],
                    'tour_description': row['tour_description'],
                    'price': row['price'],
                    'isActive': False if row['isActive'] == 0 else True,
                    'starting_date': row['starting_date'],
                    'bookingDeadline': row['booking_deadline'],
                    'day_num': row['day_num'],
                    'night_num': row['night_num'],
                    'schedule': schedule_data,
                    'service': service_data,
                    'note': row['note'],
                    'staff': random_staff,
                }
                # print(tour_data)
                # serializer = self.get_serializer(data=tour_data)
                # serializer.is_valid(raise_exception=True)  # Validate data, raise exception if invalid
                # serializer.save()
                tour = Tour.objects.create(**tour_data)

                # Associate places with the tour
                tour.places.add(*places)

            return Response({'message': 'Places created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': f'Error creating places: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TourSearchDeadlinesAPIView(generics.ListAPIView):
    queryset = Tour.objects.all()
    serializer_class = PlaceTourSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        tour = Tour.objects.all().filter(is_cancel=False).order_by('bookingDeadline')
        tour_list = self.serializer_class(tour, many=True)
        result = {'count': tour.count(), 'row': tour_list.data}

        return Response(result, status=status.HTTP_200_OK)
    
class TourHighestRatingAPIView(generics.ListAPIView):
    queryset = Tour.objects.all()
    serializer_class = PlaceTourFeedbackSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        ratings = (
            Feedback.objects.values('tour_ID')
            .annotate(average_rating=Avg('ratings'), order=Count('ratings'))
            .order_by('-average_rating')
        )

        sorted_tour = list(ratings)
        if sorted_tour == []:
            return Response({'count': 0, 'row': None}, status=status.HTTP_200_OK) 

        result_tour = []
        for i in sorted_tour:
            tour = Tour.objects.filter(
                is_cancel=False, 
                isActive=True,
                tour_ID__icontains=i['tour_ID']
            ).order_by('bookingDeadline').first()
            
            if not tour:
                continue

            tour_list = self.serializer_class(tour).data
            
            result_tour.append({
                'row': tour_list, 
                'average_rating': i['average_rating'], 
                'order': i['order']
            })

        result = {'count': len(result_tour), 'row': result_tour}

        return Response(result, status=status.HTTP_200_OK)

class TourSearchByPlaceAPIView(generics.ListAPIView):
    queryset = Tour.objects.all()
    serializer_class = TourViewSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        pass

class TourSearchByStaffIDAPIView(generics.ListAPIView):
    queryset = Tour.objects.all()
    serializer_class = PlaceTourSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        staff_ID = self.request.data.get('staff_ID')
        staff = Staff.objects.get(staff_ID=staff_ID)

        tour = Tour.objects.filter(staff=staff.pk)
        tour_lst = self.serializer_class(tour, many=True)
        return Response(tour_lst.data, status=status.HTTP_200_OK)

class TourSearchByStaffAPIView(generics.ListAPIView):
    queryset = Tour.objects.all()
    serializer_class = PlaceTourSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        auth_header = auth_header.split(" ")[1]
        # print(auth_header)
        decoded_data = jwt.decode(auth_header, options={"verify_signature": False})
        staff = decoded_data['data']['staff_ID']
        # staff = self.request.data.get('staff')

        tour = Tour.objects.filter(staff=staff, is_cancel=False)
        tour_lst = self.serializer_class(tour, many=True)
        return Response(tour_lst.data, status=status.HTTP_200_OK)

class TourDetailAPIView(views.APIView):
    queryset = Tour.objects.all()
    serializer_class = PlaceTourDetailSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        tour_ID = self.request.data.get('tour_ID')
        tour = Tour.objects.get(tour_ID=tour_ID)
        order = Order.objects.filter(tour_ID=tour_ID)

        try:            
            serializer = self.serializer_class(tour)
            result = serializer.data
            result['cus_num'] = order.count()
            return Response(result, status=status.HTTP_200_OK)
        
        except Tour.DoesNotExist:
            return Response("Không có tour", status=status.HTTP_200_OK)
    
class TourCreateAPIView(generics.CreateAPIView):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        name = self.request.data.get('name') 
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
        departure = self.request.data.get('departure') #if self.request.data.get('departure') != None else "TP. Hồ Chí Minh"
        vehicle = self.request.data.get('vehicle') #if self.request.data.get('vehicle') != None else "Máy bay"
        seat_num = self.request.data.get('seat_num') #if self.request.data.get('seat_num') != None else 30
        price = self.request.data.get('price') #if self.request.data.get('price') != None else 5979000
        isActive = self.request.data.get('isActive') if self.request.data.get('isActive') != None else False
        bookingDeadline = datetime.strptime(self.request.data.get('bookingDeadline'), "%Y_%m_%d").date() #if self.request.data.get('bookingDeadline') != None else datetime.strptime("2024_01_29", "%Y_%m_%d").date()
        day_num = self.request.data.get('day_num') #if self.request.data.get('day_num') != None else 3
        night_num = self.request.data.get('night_num') #if self.request.data.get('night_num') != None else 2
        note = self.request.data.get('note') #if self.request.data.get('note') != None else "No note"
        schedule = self.request.data.get('schedule') #if self.request.data.get('schedule') != None else ["NGÀY 01: ",
                                                                                                        # "NGÀY 02: \nBãi Sao",
                                                                                                        # "NGÀY 03: \n- Giờ bay có thể bị thay đổi bởi hãng hàng không"]
        service = self.request.data.get('service') #if self.request.data.get('service') != None else ["Bảo hiểm",
                                                                                                    #  "Hướng dẫn viên",
                                                                                                    #  "Vé tham quan","Bữa ăn"]
        place_ids = self.request.data.get('place') #if self.request.data.get('place') != None else ['P_001', 'P_002', 'P_003']
        random_staff = Staff.objects.order_by('?').first()

        places = Place.objects.filter(place_ID__in=place_ids)

        tour = {
            'tour_ID': tour_ID,
            'name': name,
            'departure': departure,
            'vehicle': vehicle,
            'seat_num': seat_num,
            'price': price,
            'isActive': isActive,
            'starting_date': starting_date,
            'bookingDeadline': bookingDeadline,
            'day_num': day_num,
            'night_num': night_num,
            'note': note,
            'schedule': json.dumps(schedule, ensure_ascii=False),
            'service': json.dumps(service, ensure_ascii=False),
            'staff': random_staff.pk,
            'places': [x.pk for x in places]
        }

        serializer = self.get_serializer(data=tour)

        if serializer.is_valid():
            serializer.save()  # Save the validated serializer data
            response_data = {'err': 0, 'msg': 'success', 'token': serializer.data}
            return Response(response_data, status=status.HTTP_201_CREATED)   
        else:
            # print(serializer.data)
            errors = serializer.errors
            return Response({'error': 1, 'msg': errors, 'token': None}, status=status.HTTP_400_BAD_REQUEST)
        
class TourUpdateAPIView(generics.UpdateAPIView):
    queryset = Tour.objects.all()
    serializer_class = TourUpdateSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        tour_ID = self.request.data.get('tour_ID')
        update_tour = Tour.objects.get(pk=tour_ID)

        staff_ID = self.request.data.get('staff')
        staff = None
        if staff_ID:
            try:
                staff = Staff.objects.get(pk=staff_ID) 
            except Staff.DoesNotExist:
                return Response({'err': 1, 'msg': 'Invalid staff ID'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            staff = update_tour.staff

        tour_data = {
            'departure': self.request.data.get('departure') if self.request.data.get('departure') not in ["", None] else update_tour.departure,
            'vehicle': self.request.data.get('vehicle') if self.request.data.get('vehicle') not in ["", None] else update_tour.vehicle,
            'seat_num': self.request.data.get('seat_num') if self.request.data.get('seat_num') not in ["", None] else update_tour.seat_num,
            'price': self.request.data.get('price') if self.request.data.get('price') not in ["", None] else update_tour.price,
            'isActive': self.request.data.get('isActive') if self.request.data.get('isActive') not in ["", None] else update_tour.isActive,
            'starting_date': datetime.strptime(self.request.data.get('starting_date'), "%Y_%m_%d").date() if self.request.data.get('starting_date') not in ["", None] else update_tour.starting_date,
            'bookingDeadline': datetime.strptime(self.request.data.get('bookingDeadline'), "%Y_%m_%d").date() if self.request.data.get('bookingDeadline') not in ["", None] else update_tour.bookingDeadline,
            'day_num': self.request.data.get('day_num') if self.request.data.get('day_num') not in ["", None] else update_tour.day_num,
            'night_num': self.request.data.get('night_num') if self.request.data.get('night_num') not in ["", None] else update_tour.night_num,
            'note': self.request.data.get('note') if self.request.data.get('note') not in ["", None] else update_tour.note,
            'schedule': json.dumps(self.request.data.get('schedule'), ensure_ascii=False) if self.request.data.get('schedule') not in ["", None] else update_tour.schedule,
            'service': json.dumps(self.request.data.get('service'), ensure_ascii=False) if self.request.data.get('service') not in ["", None] else update_tour.service,
            # 'staff': staff
        }

        serializer = self.serializer_class(data=tour_data)

        if serializer.is_valid():
            for att, value in tour_data.items():
                setattr(update_tour, att, value)

            update_tour.staff = staff
            update_tour.save()

            return Response({'err': 0}, status=status.HTTP_200_OK)
        else:
            return Response({'err': 1, 'msg': serializer.errors}, status=status.HTTP_200_OK)

class TourUpdateActiveAPIView(generics.UpdateAPIView):
    queryset = Tour.objects.all()
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        tourlst = self.queryset
        for tour in tourlst:
            if tour.starting_date + timedelta(days=tour.day_num) <= datetime.now().date():
                tour.isActive = False
                tour.save()
        return Response({'msg': "Tour updated"}, status=status.HTTP_200_OK)

class TourCancelAPIView(generics.UpdateAPIView):
    queryset = Tour.objects.all()
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):

        tour_ID = self.request.data.get('tour_ID')
        tour = Tour.objects.get(tour_ID=tour_ID)

        #xét condition
        orders = Order.objects.filter(tour_ID=tour.pk)
        for order in orders:
            order.is_cancel = True
            order.cancel_datetime = datetime.now()
            order.cancel_percent = 0
            order.save()

        tour.is_cancel = True
        tour.isActive = False
        tour.save()

        return Response({'err': 0, 'msg': "cancel success"}, status=status.HTTP_200_OK)


class ReportTourCountAPIView(views.APIView):
    queryset = Tour.objects.all()
    serializer_class = PlaceTourSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        year = int(self.request.data.get("year"))

        tours_by_month = Tour.objects.filter(starting_date__year=year).annotate(
            month=TruncMonth('starting_date')
        ).values('month').annotate(count=Count('tour_ID')).order_by('month')

        # Count tours by quarter
        tours_by_quarter = Tour.objects.filter(starting_date__year=year).annotate(
            quarter=TruncQuarter('starting_date')
        ).values('quarter').annotate(count=Count('tour_ID')).order_by('quarter')

        # Prepare month names and quarter numbers
        month_names = [calendar.month_name[month['month'].month] for month in tours_by_month]
        quarter_numbers = [(quarter['quarter'].month - 1) // 3 + 1 for quarter in tours_by_quarter]

        # Format the result with month and quarter keys
        result = {
            "tours_by_month": [{"month": month_name, "count": month['count']} for month_name, month in zip(month_names, tours_by_month)],
            "tours_by_quarter": [{"quarter": quarter_number, "count": quarter['count']} for quarter_number, quarter in zip(quarter_numbers, tours_by_quarter)],
            "tours_by_year": Tour.objects.filter(starting_date__year=year).count()
        }

        return Response(result, status=status.HTTP_200_OK)