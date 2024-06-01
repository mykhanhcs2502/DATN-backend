from django.urls import path
from requestTour.views import RequestCreateAddAPI, RequestCreateCancelAPI, RequestCreateEditAPI, RequestGetByStaffAPIView
from staff.views import *
from tour.views import TourSearchByStaffAPIView
from . import views

urlpatterns = [
    path('add_all/', StaffAddAllAPIView.as_view(), name='staff_add_all'),
    path('delete_all/', StaffDeleteAllAPIView.as_view(), name='staff_delete_all'), 
    path('login', StaffLoginAPIView.as_view(), name='staff login'), 
    path('update_pass_first_login', StaffFirstLoginAPIView.as_view()),
    
    path('tour/get_all', TourSearchByStaffAPIView.as_view(), name='tour_for_staff'), 

    path('request/get_all', RequestGetByStaffAPIView.as_view()),
    path('request/add/add', RequestCreateAddAPI.as_view()),
    path('request/edit/add', RequestCreateEditAPI.as_view()),
    path('request/cancel/add', RequestCreateCancelAPI.as_view()),
]