from django.conf import settings
from ..authentication.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail


def send_mail_user(request, serializer):
    user = request.data.get('user', {})
    email = user['email']
    users = User.objects.filter(email=email)
    users.update(is_active=False)
    url_param = get_current_site(request).domain
    email = user['email']
    send_mail(
        'Email-verification',
        'Click here to verify your account {}/api/users/verify?token={}'
        .format(url_param, serializer.data['token']),
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )
    info = """You have successfully been registered,please check \
        your email for confirmation"""
    email_verify = {"Message": info, "token": serializer.data['token']}
    return email_verify
