from django.urls import path
from order_feedback.views import FeedbackTourAPIView, OrderOfTourAPIView, OrderTourTypeAPIView
from tour.views import *
from . import views

urlpatterns = [
    path('place/add_all/', PlaceAddAllAPIView.as_view(), name = 'add_places_api'),
    path('place/images/add_all/', PlaceImagesAddAllAPIView.as_view(), name='place_images_add_all'),
    path('place/get_all', PlaceAllAPIView.as_view(), name='place all'),
    path('place/get_by_condition', PlaceGetAllConditionAPIView.as_view(), name='place get by condition'), 

    path('tour/add_all/', TourAddAllAPIView.as_view(), name='tour_add_all'),
    path('tour/delete_all/', TourDeleteAllAPIView.as_view(), name='tour delete all'),
    path('tour/get_by_id', TourDetailAPIView.as_view(), name='tour_detail'), 
    path('tour/order/get_all', OrderOfTourAPIView.as_view(), name='order_of_tour'),  
    path('tour/type/order/count', OrderTourTypeAPIView.as_view(), name='order count tour type'),
    path('tour/type/feedback/get_all', FeedbackTourAPIView.as_view(), name='feedback'),
    
    path('internal/tour/add', TourCreateAPIView.as_view(), name='tour_add'),
]