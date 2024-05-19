from django.urls import path
from customer.views import *
from tour.views import *
from order_feedback.views import OrderOfCustomerAPIView, FeedbackAddAPIView
from customer.views import ForgetPassword
from customer.views import ChangePassword
from . import views

urlpatterns = [
    path('customer/add/', CustomerCreate.as_view(), name='create_customer'),
    path('customer/login', CustomerLoginAPIView.as_view(), name='get_customer'),
    path('customer/forget_pass/', ForgetPassword.as_view(), name = 'forget_pass'),
    path('customer/change_pass/<token>/', ChangePassword.as_view(), name = 'change_pass'),
    path('customer/add_all/', CustomerAddAllAPIView.as_view(), name='add_customers_api'),
    path('customer/delete_all/', CustomerDeleteAllAPIView.as_view(), name='customer_delete_all'),
    path('customer/tour/condition', ToursGetAllConditionAPIView.as_view(), name='tour_get_condition'),
    path('customer/tour/name', TourGetByNameAPIView.as_view(), name='tour_get_name'),
    path('customer/tour/highest_ratings', TourHighestRatingAPIView.as_view(), name='tour_highest_ratings'),
    path('customer/order/get_all', OrderOfCustomerAPIView.as_view(), name='order of customer'),
    path('customer/feedback/add', FeedbackAddAPIView.as_view()),

    path('get_current', GetCurrentAPI.as_view(), name='get_info'),
    path('auth/refreshToken', AuthRefreshTokenAPI.as_view()),
]