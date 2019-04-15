from django.conf import settings
from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.generics import (
    RetrieveUpdateAPIView,
    GenericAPIView,
    ListAPIView,
    UpdateAPIView)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer,
    ResetPasswordSerializer
)
from ..profiles.serializers import UserListSerializer
from ..core import registration_utils, login_utils
import jwt
from .models import User


class RegistrationAPIView(APIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})
        registration_utils.validate_registration(user)

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(registration_utils.send_mail_user(request, serializer),
                        status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})
        login_utils.validate_login(user)

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class VerifyAccount(GenericAPIView):
    permission_classes = (AllowAny, )
    serializer_class = UserSerializer

    def get(self, request, format=None):
        token = request.query_params.get('token')
        payload = jwt.decode(token, settings.SECRET_KEY)
        email = payload['email']
        user = User.objects.filter(email=email)
        user.update(is_active=True)
        return \
            HttpResponseRedirect('https://ah-front-end-groot.herokuapp.com/')


class ResetPasswordView(RetrieveUpdateAPIView):
    """
        Allows user to rrecieve  a reset passowrd link with a token on
        an email
    """
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer_data = request.data.get("user", {})
        serializer = self.serializer_class(data=serializer_data)
        serializer.is_valid(raise_exception=True)
        data = {
            "Message": "Please check your email a link has been sent to you"
        }
        return Response(data, status=status.HTTP_200_OK)

    def retrieve(self, request, token, *args, **kwargs):
        """
        This allows one to retrive the token from the end point
        after it has sent from the user mail
        """
        msg = {'token': token}
        return Response(msg, status=status.HTTP_200_OK)


class ChangePasswordView(UpdateAPIView):
    """
        Change password of the user endpoint
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})
        """
        This method gets user data and passes
        the token of the user
        """
        password = request.data.get('user')['password']

        password2 = request.data.get('user')['confirm_password']
        if password != password2:
            return Response({"message": "Password don't Match"})

        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        msg = {'Message': 'Your password has been succesfully updated'}
        return Response(msg, status=status.HTTP_200_OK)


class ListUserView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserListSerializer
    queryset = User.objects.all()
