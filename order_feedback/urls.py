from django.urls import path
from order_feedback.views import *
from . import views

urlpatterns = [
    path('order/add_all/', OrderAddAllViewAPI.as_view(), name='order_add_all'),
    path('order/delete_all/', OrderDeleteAllAPIView.as_view(), name='order_delete_all'), 
    path('order/get_by_id', OrderGetByIDAPIView.as_view(), name='order'),
    path('order/add', OrderAddAPIView.as_view()),
    path('order/update', OrderUpdateAPIView.as_view()),
    path('order/cancel', OrderCancelAPIView.as_view()),

    path('feedback/add_all/', FeedbackAddAllAPIView.as_view(), name='feedback_add_all'),
    path('feedback/delete_all/', FeedbackDeleteAllAPIView.as_view(), name='feedback_delete_all'),
]