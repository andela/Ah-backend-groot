from django.urls import path
from .views import (
    RetrieveUpdateProfileView,
    ListProfileView,
    FollowProfileView,
    FollowersListView,
    FollowingListView,
    ReadingStatsView
)

urlpatterns = [
    path('profiles/<str:username>/', RetrieveUpdateProfileView.as_view()),
    path('profiles/', ListProfileView.as_view()),
    path('profiles/<str:username>/follow/', FollowProfileView.as_view()),
    path('profiles/<str:username>/followers/', FollowersListView.as_view()),
    path('profiles/<str:username>/following/', FollowingListView.as_view()),
    path('profile/<username>/read_stats/', ReadingStatsView.as_view())
]
