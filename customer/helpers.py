from django.core.mail import send_mail
from django.conf import settings

def send_forget_password_mail(email, token):
    subject = 'Reset password link'
    message = f'Xin chào, hãy nhấn vào link dưới đây để thay đổi mật khẩu http://localhost:3000/auth/reset_pass2/{token}/'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True