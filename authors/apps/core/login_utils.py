
import re
from rest_framework import serializers


def validate_login(data):
    email = data.get('email', None)
    password = data.get('password', None)

    if not email:
        raise serializers.ValidationError(
            {
                'error':
                'Email field is required'
            }
        )

    if not password:
        raise serializers.ValidationError(
            {
                'error':
                'Password field is required'
            }
        )

    validate_email(email)


def validate_email(email):
    if not re.search(r"([\w\.-]+)@([\w\.-]+)(\.[\w\.]+$)", email):
        raise serializers.ValidationError(
            {
                'error':
                'Please enter a valid email address'

            }
        )
