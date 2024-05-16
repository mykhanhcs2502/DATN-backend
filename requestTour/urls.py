from django.urls import path
from order_feedback.views import ReportCustomerCountAPIView, ReportIncomeAPIView
from requestTour.views import *
from tour.views import ReportTourCountAPIView
from . import views

urlpatterns = [
    path('request/add_all/', RequestAddAllAPI.as_view()),
    path('request/delete_all/', RequestDeleteAllAPIView.as_view()),    
    path('request/get_by_id', RequestGetByIDAPIView.as_view()),

    path('report/tour/count', ReportTourCountAPIView.as_view()),
    path('report/customer/count', ReportCustomerCountAPIView.as_view()),
    path('report/income/count', ReportIncomeAPIView.as_view())
]