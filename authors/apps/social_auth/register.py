import os
from django.contrib.auth import authenticate
from authors.apps.authentication.models import User


def register_user(email, name):
    user = User.objects.filter(email=email)
    password = os.environ.get('SOCIAL_PASSWORD')
    if not user.exists():
        user = {
            'username': name, 'email': email, 'password': password}
        User.objects.create_user(**user)
        new_user = authenticate(email=email, password=password)
        return new_user.token
    else:
        User.objects.filter(email=email)
        registered_user = authenticate(email=email, password=password)
        return registered_user.token
