from rest_framework import serializers
from authors.apps.social_auth.facebook_auth import FacebookAuthHandler
from authors.apps.social_auth.twitter_auth import TwitterAuthHandler
from authors.apps.social_auth.google_auth import GoogleAuthHandler
from authors.apps.social_auth.register import register_user


class FacebookAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):

        user_data = FacebookAuthHandler.validate(auth_token)
        try:
            user_data['email']
        except Exception:
            raise serializers.ValidationError(
                'The token is invalid or expired. Please login again.'
            )

        email = user_data['email']
        name = user_data['name']

        return register_user(email=email, name=name)


class TwitterAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):

        user_info = TwitterAuthHandler.validate(auth_token)
        try:
            user_info['email']
        except Exception:
            raise serializers.ValidationError(
                'The token is invalid or expired. Please login again.'
            )

        email = user_info['email']
        name = user_info['name']

        return register_user(email=email, name=name)


class GoogleAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):

        user_data = GoogleAuthHandler.validate(auth_token)
        try:
            user_data['email']
        except Exception:
            raise serializers.ValidationError(
                'The token is invalid or expired. Please login again.'
            )

        email = user_data['email']
        name = user_data['name']

        return register_user(email=email, name=name)



