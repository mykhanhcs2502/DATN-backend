from django.urls import path
from manager.views import *
from requestTour.views import RequestAcceptAPIView, RequestAllAPIView, RequestGetByStaffIDAPIView
from manager.views import StaffGetByIDAPIView, StaffChangeActivateAPIView
from tour.views import TourSearchByStaffIDAPIView, TourUpdateAPIView

from . import views

urlpatterns = [
    path('manager/add_all/', ManagerAddAllAPIView.as_view(), name='manager_add_all'),
    path('manager/login', ManagerLoginAPIView.as_view()),
    path('manager/delete', ManagerDeleteAllAPIView.as_view()),
    path('manager/staff/add', StaffAddAPIView.as_view()),
    path('manager/staff/get_all', StaffAllAPIView.as_view(), name='staff all'),
    path('manager/staff/get_by_id', StaffGetByIDAPIView.as_view()),
    path('manager/staff/update_info', StaffUpdateInfoAPIView.as_view()),
    path('manager/tour/staffID', TourSearchByStaffIDAPIView.as_view()),
    path('manager/request/staffID', RequestGetByStaffIDAPIView.as_view()),
    path('manager/request/get_all', RequestAllAPIView.as_view()),
    path('manager/tour/update', TourUpdateAPIView.as_view(), name='tour_update'),
    path('manager/request/reply', RequestAcceptAPIView.as_view()),
    path('manager/staff/change_active', StaffChangeActivateAPIView.as_view()),
]