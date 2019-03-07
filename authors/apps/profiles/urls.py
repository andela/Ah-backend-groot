from django.urls import path
from .views import (
    RetrieveUpdateProfileView,
    ListProfileView)

urlpatterns = [
    path('profiles/<str:username>/', RetrieveUpdateProfileView.as_view()),
    path('profiles/', ListProfileView.as_view()),
]
