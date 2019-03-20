from rest_framework import serializers
from authors.apps.social_auth import facebook_auth, google_auth, twitter_auth
from authors.apps.social_auth.register import register_user


class AuthSerializer(serializers.Serializer):

    def validate_token(self, key, user_data):
        try:
            user_data[key]
        except Exception:
            raise serializers.ValidationError(
                'The token is invalid or expired. Please login again.'
            )

        email = user_data['email']
        name = user_data['name']

        return register_user(email=email, name=name)


class FacebookAuthSerializer(AuthSerializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):

        user_data = facebook_auth.FacebookAuthHandler\
            .validate_facebook_auth_token(auth_token)

        return self.validate_token('id', user_data)


class GoogleAuthSerializer(AuthSerializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):

        user_data = google_auth.GoogleAuthHandler\
            .validate_google_auth_token(auth_token)

        return self.validate_token('sub', user_data)


class TwitterAuthSerializer(AuthSerializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):

        user_info = twitter_auth.TwitterAuthHandler\
            .validate_twitter_auth_tokens(auth_token)

        return self.validate_token('id_str', user_info)
