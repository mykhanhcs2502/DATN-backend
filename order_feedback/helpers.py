from django.core.mail import send_mail
from django.conf import settings

def cancel_tour_mail(email, days_until_tour, cancel_percent):
    subject = 'Email xác nhận hủy tour'
    message = (f'Xin chào, quý khách vừa hủy tour trước ngày khởi hành {days_until_tour} ngày.'
           f'Vì vậy, quý khách sẽ phải chịu {cancel_percent}% tiền tour.\n'
           'Vui lòng kiểm tra tài khoản ngân hàng trong 15 ngày tới.\n'
           'Hẹn gặp lại quý khách ở những chuyến đi sau!')
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True