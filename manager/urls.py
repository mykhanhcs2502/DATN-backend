from django.urls import path
from manager.views import *
from requestTour.views import RequestAcceptAPIView, RequestAllAPIView, RequestGetByStaffIDAPIView
from manager.views import StaffGetByIDAPIView, StaffChangeActivateAPIView
from tour.views import TourSearchByStaffIDAPIView, TourUpdateAPIView

from . import views

urlpatterns = [
    path('add_all/', ManagerAddAllAPIView.as_view(), name='manager_add_all'),
    path('login', ManagerLoginAPIView.as_view()),
    path('delete', ManagerDeleteAllAPIView.as_view()),
    path('staff/add', StaffAddAPIView.as_view()),
    path('staff/get_all', StaffAllAPIView.as_view(), name='staff all'),
    path('staff/get_by_id', StaffGetByIDAPIView.as_view()),
    path('staff/update_info', StaffUpdateInfoAPIView.as_view()),
    path('tour/staffID', TourSearchByStaffIDAPIView.as_view()),
    path('request/staffID', RequestGetByStaffIDAPIView.as_view()),
    path('request/get_all', RequestAllAPIView.as_view()),
    path('tour/update', TourUpdateAPIView.as_view(), name='tour_update'),
    path('request/reply', RequestAcceptAPIView.as_view()),
    path('staff/change_active', StaffChangeActivateAPIView.as_view()),
]