from datetime import datetime
import random
from rest_framework import generics
from order_feedback.models import Order, Feedback
from customer.models import Customer
from tour.models import Tour
from order_feedback.serializer import *
from tour.serializer import TourOrderSerializer
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework import views
from django.db.models.functions import TruncMonth, TruncQuarter
from django.db.models import Sum, F
import calendar
import pandas as pd
import jwt
from order_feedback.helpers import cancel_tour_mail

class OrderAddAPIView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderAddSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        auth_header = self.request.headers.get('Authorization')

        user_ID = None
        if not auth_header:
            user_ID = None

        try:
            token = auth_header.split(" ")[1]
            decoded_data = jwt.decode(token, options={"verify_signature": False})
            customer_ID = decoded_data['data'].get('customer_ID')
            if customer_ID is not None:
                email = decoded_data['data']['email']
                user_ID = Customer.objects.get(email=email).pk
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Customer.DoesNotExist, KeyError):
            user_ID = None

        pay_method = self.request.data.get('pay_method')
        email = self.request.data.get('email')
        name = self.request.data.get('username')
        phone = self.request.data.get('phone')
        note = self.request.data.get('note')
        ticket_num = self.request.data.get('ticket_num')
        tour_ID = self.request.data.get('tour_ID')
        
        # thiếu ticket_num và tour_ID
        # thiếu payment_method

        i = Order.objects.count()
        while Order.objects.filter(order_ID=f"O_{i:03}").exists():
            i += 1

        print(tour_ID)
        new_order = {
            'order_ID': f"O_{i:03}",
            'pay_method': pay_method,
            'user_ID': user_ID,
            'name': name,
            'email': email,
            'phone_no': phone,
            'note': note if note else "No note",
            'ticket_num': ticket_num,
            'tour_ID': Tour.objects.get(tour_ID=tour_ID).pk
        }

        serializer = self.serializer_class(data=new_order)
        if serializer.is_valid():
            serializer.save()
            return Response({'err': 0, 'msg': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'err': 1, 'msg': serializer.errors}, status=status.HTTP_200_OK)

class OrderAddAllViewAPI(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderAddSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        file_order = 'order_feedback/sqlScript/Order.xlsx'
        data = pd.read_excel(file_order)

        for _, row in data.iterrows():
            userID = Customer.objects.get(customer_ID=row['user_ID'])
            tourID = Tour.objects.filter(tour_ID__contains=row['tour_ID'])
            tourID = random.choice(tourID)

            order_data = {
                'order_ID': row['order_ID'],
                'pay_method': row['pay_method'],
                'user_ID': userID.pk,
                'email': row['email'],
                'name': row['name'],
                'phone_no': row['phone_no'],
                'date_time': row['date_time'],
                'note': row['note'],
                'ticket_num': row['ticket_num'],
                'tour_ID': tourID.pk
            }
            serializer = OrderAddSerializer(data=order_data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_200_OK)

        return Response({'message': 'Order created successfully'}, status=status.HTTP_201_CREATED)
    
class OrderDeleteAllAPIView(generics.DestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderAddSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def delete(self, request, *args, **kwargs):
        # Delete all Staff instances
        deleted_count, _ = self.get_queryset().delete()
        return Response({'message': f'{deleted_count} Order deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

class OrderOfTourAPIView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderOfTourSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        tourID = self.request.data.get('tour_ID')
        orders = Order.objects.filter(tour_ID=tourID)

        if orders.exists(): 
            tour = Tour.objects.get(tour_ID=tourID)
            if tour.isActive == 1:
                rows = [] 
                for order in orders:
                    order_serializer = self.serializer_class(order)
                    rows.append({'order': order_serializer.data, 'feedback': None})

                return Response({'err': 0, 'count': orders.count(), 'row': rows}, status=status.HTTP_200_OK)
            
            # user_ids = orders.values_list('user_ID', flat=True)
            # feedbacks = Feedback.objects.filter(user_ID__in=user_ids)
            # feedback_dict = {feedback.user_ID: feedback for feedback in feedbacks}

            rows = [] 
            for order in orders:
                order_serializer = self.serializer_class(order)
                feedback = Feedback.objects.filter(order_ID=order.order_ID)
                if feedback.exists():
                    feedback_serializer = FeedbackViewSerializer(feedback.first())
                    rows.append({'order': order_serializer.data, 'feedback': feedback_serializer.data})
                else:
                    rows.append({'order': order_serializer.data, 'feedback': None})

            return Response({'err': 0, 'count': orders.count(), 'row': rows}, status=status.HTTP_200_OK)
        else:
            return Response({'err': 1, 'count': 0}, status=status.HTTP_200_OK)
        
class OrderGetByIDAPIView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderViewSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        order_ID = self.request.data.get('order_ID')
        orders = Order.objects.get(order_ID=order_ID)

        if orders is not None: 
            order = self.serializer_class(orders)
            result = order.data
            if Feedback.objects.filter(order_ID=order_ID).count() != 0:
                result['Feedback'] = FeedbackViewSerializer(Feedback.objects.get(order_ID=order_ID)).data
            else:
                result['Feedback'] = None
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response("No order", status=status.HTTP_200_OK)
        
class OrderTourTypeAPIView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderOfTourSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        tourID = self.request.data.get('tour_ID')
        orders = Order.objects.filter(tour_ID__tour_ID__icontains=tourID)

        if orders.exists(): 
            return Response({'err': 0, 'count': orders.count()}, status=status.HTTP_200_OK)
        else:
            return Response({'err': 1, 'count': 0}, status=status.HTTP_200_OK)
        
class OrderOfCustomerAPIView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderOfCustomerSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization').split(" ")[1]
        decoded_data = jwt.decode(auth_header, options={"verify_signature": False})
        customer_ID = decoded_data['data']['customer_ID']
        orders = Order.objects.filter(user_ID=customer_ID)
        
        if orders.exists(): 
            # user_ids = orders.values_list('user_ID', flat=True)
            # feedbacks = Feedback.objects.filter(user_ID__in=user_ids)
            # feedback_dict = {feedback.user_ID: feedback for feedback in feedbacks}

            rows = [] 
            for order in orders:
                order_serializer = self.serializer_class(order)
                feedback = Feedback.objects.filter(order_ID=order.order_ID)
                if feedback.exists():
                    feedback_serializer = FeedbackSerializer(feedback.first())
                    tour_serializer = TourOrderSerializer(Tour.objects.get(tour_ID=order.tour_ID.pk))
                    rows.append({'order': order_serializer.data, 'feedback': feedback_serializer.data, 'tour': tour_serializer.data})
                else:
                    tour_serializer = TourOrderSerializer(Tour.objects.get(tour_ID=order.tour_ID.pk))
                    rows.append({'order': order_serializer.data, 'feedback': None, 'tour': tour_serializer.data})  

            return Response({'err': 0, 'count': orders.count(), 'row': rows}, status=status.HTTP_200_OK)
        else:
            return Response({'err': 1, 'count': 0}, status=status.HTTP_200_OK)
        
class OrderUpdateAPIView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderUpdateSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        order_ID = self.request.data.get('order_ID')

        update_attribute = {
            'email': self.request.data.get('email') if self.request.data.get('email') not in ["", None] else None,
            'name': self.request.data.get('name') if self.request.data.get('name') not in ["", None] else None,
            'phone_no': self.request.data.get('phone_no') if self.request.data.get('phone_no') not in ["", None] else None,
            'note': self.request.data.get('note') if self.request.data.get('note') not in ["", None] else None,
            'is_refund': self.request.data.get('is_refund') if self.request.data.get('is_refund') not in ["", None] else None
        }

        serializer = self.serializer_class(data=update_attribute)

        if serializer.is_valid():
            update_order = Order.objects.get(pk=order_ID)

            for att, value in update_attribute.items():
                if value is not None:
                    setattr(update_order, att, value)

            update_order.save()

            return Response({'err': 0}, status=status.HTTP_200_OK)
        else:
            return Response({'err': 1, 'msg': serializer.errors}, status=status.HTTP_200_OK)

class OrderCancelAPIView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderCancelSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        # auth_header = request.headers.get('Authorization').split(" ")[1]
        # decoded_data = jwt.decode(auth_header, options={"verify_signature": False})
        # tmp = {'type': None, 'id': None, 'email': None}
        # if decoded_data['data'].get('customer_ID'):
        #     tmp['type'] = "customer"
        #     tmp['id'] = decoded_data['data']['customer_ID']
        #     tmp['email'] = decoded_data['data']['email']
        # else:
        #     tmp['type'] = "staff"
        #     tmp['id'] = decoded_data['data']['staff_ID']
        #     tmp['email'] = decoded_data['data']['email']

        order_ID = self.request.data.get('order_ID')
        order = Order.objects.get(order_ID=order_ID)
        
        cancel_percent = 100
        cancel_date = datetime.now()
        starting_date = order.tour_ID.starting_date
        starting_date = datetime.combine(starting_date, datetime.min.time())

        days_until_tour = (starting_date - cancel_date).days

        if days_until_tour >= 15:
            cancel_percent = 30
        elif days_until_tour >= 8:
            cancel_percent = 50
        elif days_until_tour >= 2:
            cancel_percent = 80

        update_attribute = {
            'is_cancel': True,
            'cancel_datetime': cancel_date,
            'cancel_percent': cancel_percent
        }

        serializer = self.serializer_class(data=update_attribute)

        if serializer.is_valid():
            for att, value in update_attribute.items():
                if value is not None:
                    setattr(order, att, value)

            order.save()
            cancel_tour_mail(order.email, days_until_tour, cancel_percent)

            return Response({'err': 0, 'email': order.email}, status=status.HTTP_200_OK)
        else:
            return Response({'err': 1, 'msg': serializer.errors}, status=status.HTTP_200_OK)        
        
class FeedbackDeleteAllAPIView(generics.DestroyAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def delete(self, request, *args, **kwargs):
        # Delete all Staff instances
        deleted_count, _ = self.get_queryset().delete()
        return Response({'message': f'{deleted_count} Order deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

class FeedbackAddAllAPIView(generics.CreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *arg, **kwargs):
        file_feedback = 'order_feedback/sqlScript/Feedback.xlsx'
        data = pd.read_excel(file_feedback)

        for _, row in data.iterrows():
            userID = Customer.objects.get(customer_ID=row['user_ID'])
            order = Order.objects.filter(user_ID=row['user_ID']).order_by('?').first()
            tourID = order.tour_ID.pk.split('_')[0]
            feedback_data = {
                'feedback_ID': row['feedback_ID'],
                'ratings': row['ratings'],
                'reviews': row['reviews'],
                'datetime': row['datetime'],
                'user_ID': userID.pk,
                'tour_ID': tourID,
                'order_ID': order.pk,
            }

            serializer = self.get_serializer(data=feedback_data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response({serializer.errors}, status=status.HTTP_200_OK)

        return Response({'message': 'Feedback created successfully'}, status=status.HTTP_201_CREATED)
    
class FeedbackTourAPIView(views.APIView):
    queryset = Feedback.objects.all()
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *arg, **kwargs):
        tour_ID = self.request.data.get('tour_ID')

        feedback = Feedback.objects.filter(tour_ID=tour_ID)
        serializer = FeedbackViewSerializer(feedback, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
class FeedbackAddAPIView(generics.CreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        auth_header = self.request.headers.get('Authorization')

        if auth_header is None:
            return Response({'err': 1, 'msg': 'Authorization header missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = auth_header.split(" ")[1]
            decoded_data = jwt.decode(token, options={"verify_signature": False})
            customer_ID = decoded_data['data']['customer_ID']
            customer = Customer.objects.get(customer_ID=customer_ID)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError, Customer.DoesNotExist):
            return Response({'err': 1, 'msg': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        
        # print(self.request.data.get('payload')['tour_ID'])
        # print(self.request.data.get('ratings'))

        i = 1
        while Feedback.objects.filter(feedback_ID=f"F_{i:03}").exists():
            i+=1

        feedback_ID = f"F_{i:03}"
        tour_ID = self.request.data.get('tour_ID').split("_")[0]
        feedback_data = {
                'feedback_ID': feedback_ID,
                'ratings': self.request.data.get('ratings'),
                'reviews': self.request.data.get('reviews'),
                # 'datetime': row['datetime'],
                'user_ID': customer.pk,
                'tour_ID': tour_ID,
                'order_ID': Order.objects.get(order_ID=self.request.data.get('order_ID')).pk,
        }

        serializer = self.serializer_class(data=feedback_data)
        if serializer.is_valid():
            serializer.save()
            return Response({'err': 0, 'msg': serializer.data}, status=status.HTTP_200_OK)
        
        return Response({'err': 0, 'msg': serializer.errors}, status=status.HTTP_200_OK)

class ReportCustomerCountAPIView(views.APIView):
    queryset = Order.objects.all()
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        year = int(self.request.data.get("year"))

        orders_by_month = Order.objects.filter(date_time__year=year).annotate(
            month=TruncMonth('date_time')
        ).values('month').annotate(total=Sum('ticket_num')).order_by('month')

        # Count tours by quarter
        orders_by_quarter = Order.objects.filter(date_time__year=year).annotate(
            quarter=TruncQuarter('date_time')
        ).values('quarter').annotate(total=Sum('ticket_num')).order_by('quarter')

        # Prepare month names and quarter numbers
        month_names = [calendar.month_name[month['month'].month] for month in orders_by_month]
        quarter_numbers = [(quarter['quarter'].month - 1) // 3 + 1 for quarter in orders_by_quarter]

        # Format the result with month and quarter keys
        result = {
            "orders_by_month": [{"month": month_name, "total": month['total']} for month_name, month in zip(month_names, orders_by_month)],
            "orders_by_quarter": [{"quarter": quarter_number, "total": quarter['total']} for quarter_number, quarter in zip(quarter_numbers, orders_by_quarter)],
            "orders_by_year": Order.objects.filter(date_time__year=year).aggregate(total=Sum('ticket_num'))['total']
        }

        return Response(result, status=status.HTTP_200_OK)
    
class ReportIncomeAPIView(views.APIView):
    queryset = Order.objects.all()
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        year = int(self.request.data.get("year"))

        income_by_month = Order.objects.filter(date_time__year=year).annotate(
            month=TruncMonth('date_time')
        ).values('month').annotate(total=Sum(F('ticket_num') * F('tour_ID__price'))).order_by('month')

        # Count tours by quarter
        income_by_quarter = Order.objects.filter(date_time__year=year).annotate(
            quarter=TruncQuarter('date_time')
        ).values('quarter').annotate(total=Sum(F('ticket_num') * F('tour_ID__price'))).order_by('quarter')

        # Prepare month names and quarter numbers
        month_names = [calendar.month_name[month['month'].month] for month in income_by_month]
        quarter_numbers = [(quarter['quarter'].month - 1) // 3 + 1 for quarter in income_by_quarter]

        # Format the result with month and quarter keys
        result = {
            "orders_by_month": [{"month": month_name, "total": month['total']} for month_name, month in zip(month_names, income_by_month)],
            "orders_by_quarter": [{"quarter": quarter_number, "total": quarter['total']} for quarter_number, quarter in zip(quarter_numbers, income_by_quarter)],
            "orders_by_year": Order.objects.filter(date_time__year=year).aggregate(total=Sum(F('ticket_num') * F('tour_ID__price')))['total']
        }

        return Response(result, status=status.HTTP_200_OK)