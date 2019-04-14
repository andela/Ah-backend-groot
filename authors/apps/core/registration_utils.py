from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
import re
from rest_framework import serializers

from ..authentication.models import User


def validate_registration(data):
    username = data.get('username', None)
    email = data.get('email', None)
    password = data.get('password', None)

    if not (username or email or password):
        raise serializers.ValidationError(
            {
                'input fields':
                'All fields are required'
            }
        )

    validate_username_isnot_empty(username)

    validate_username_length(username)

    validate_username(username)

    validate_email(email)

    valid_password(password)

    return{"username": username, "email": email, "password": password}


def validate_email(email):
    if not re.search(r"([\w\.-]+)@([\w\.-]+)(\.[\w\.]+$)", email):
        raise serializers.ValidationError(
            {
                'Email':
                'Please enter a valid email address'

            }
        )


def validate_username_length(username):
    if len(username) < 4:
        raise serializers.ValidationError(
            {
                'username':
                'Please the username should be at'
                'least 4 characters'
            }
        )


def validate_username_isnot_empty(username):
    if not username:
        raise serializers.ValidationError(
            {
                'input fields':
                'Please input a username'
            }
        )


def validate_username(username):
    if not re.match(r"^[A-Za-z]+[\d\w_]+", username):
        raise serializers.ValidationError(

            {
                'username':
                'Username should start with letters'
            }
        )


def valid_password(password):
    long_password = (len(password) >= 8)
    atleast_number = re.search("[0-9]", password)
    Capital_letters = re.search("[A-Z]", password)

    if (not long_password or not atleast_number or not Capital_letters):
        raise serializers.ValidationError(
            {'password': 'Password should contain at'
             'least 8 characters uppercase, number'})


def send_mail_user(request, serializer):
    user = request.data.get('user', {})
    email = user['email']
    users = User.objects.filter(email=email)
    users.update(is_active=False)
    url_param = get_current_site(request).domain
    email = user['email']
    body = "Click here to verify your account {}/api/users/verify/?token={}"

    send_mail('Email-verification',
              body
              .format(url_param, serializer.data['token']),
              settings.EMAIL_HOST_USER,
              [email],
              fail_silently=False,)
    info = "You have successfully been registered, \
           please check your email for confirmation"
    refined_info = re.sub('  +', ' ', info)
    email_verify = {"Message": refined_info, "token": serializer.data['token']}
    return email_verify


def send_an_email(receiver_email, body, article_link, sender):
    message = render_to_string(body, {
        "article_link": article_link,
        "sender": sender})
    email = EmailMessage(
        'Authors Haven',
        message,
        to=[receiver_email],
    )
    email.content_subtype = "html"
    email.send(fail_silently=False)
