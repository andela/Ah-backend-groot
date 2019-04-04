from django.contrib.auth import authenticate
from authors.apps.authentication.models import User


def register_user(email, name):
    user = User.objects.filter(email=email)

    if not user.exists():
        user = {
            'username': name, 'email': email, 'password': 'XXXXXXXX'}
        User.objects.create_user(**user)
        new_user = authenticate(email=email, password="XXXXXXXX")
        return new_user.token
    else:
        User.objects.filter(email=email)
        registered_user = authenticate(email=email, password="XXXXXXXX")
        return registered_user.token
