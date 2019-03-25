from django.contrib.auth import authenticate
from authors.apps.authentication.models import User
from django.conf import settings

def register_user(email, name):
    user = User.objects.filter(email=email)
    if not user.exists():
        user = {
            'username': name, 'email': email, 'password': 'XXXXXXXX'}
        User.objects.create_user(**user)
        new_user = authenticate(email=email, password="XXXXXXXX")
        return {
            'email': new_user.email,
            'username': new_user.username,
            'token': new_user.token,
        }
    else:
        User.objects.filter(email=email)
        registered_user = authenticate(email=email, password="XXXXXXXX")
        return {
            'email': registered_user.email,
            'username': registered_user.username,
            'token': registered_user.token,
        }
