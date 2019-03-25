from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView,
    VerifyAccount, ResetPasswordView, ChangePasswordView, ListUserView,
)


urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    path('users/', RegistrationAPIView.as_view()),
    path('users/list/', ListUserView.as_view()),
    path('users/login/', LoginAPIView.as_view()),
    path('users/verify/', VerifyAccount.as_view()),
    path('password-reset/', ResetPasswordView.as_view()),
    path('password-reset/<token>/', ResetPasswordView.as_view()),
    path('password/reset/done/', ChangePasswordView.as_view()),
]
