from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import AllowAny
from authors.apps.authentication.renderers import UserJSONRenderer
from authors.apps.social_auth.serializers import (FacebookAuthSerializer,
                                                  GoogleAuthSerializer,
                                                  TwitterAuthSerializer)


class FacebookSocialAuthView(ListCreateAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)

    def post(self, request):
        serializer_class = FacebookAuthSerializer
        user = request.data.get('user', {})
        serializer = serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GoogleSocialAuthView(ListCreateAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)

    def post(self, request):
        serializer_class = GoogleAuthSerializer
        user = request.data.get('user', {})
        serializer = serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TwitterSocialAuthView(ListCreateAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)

    def post(self, request):
        serializer_class = TwitterAuthSerializer
        user = request.data.get('user', {})
        serializer = serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
