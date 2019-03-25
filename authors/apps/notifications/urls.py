from django.urls import path
from .views import SubscriptionView, NotificationView, ListNotificationView


urlpatterns = [
    path('notifications/subscribe/<str:type>/', SubscriptionView.as_view()),
    path('notifications/<int:id>/', NotificationView.as_view()),
    path('notifications/', ListNotificationView.as_view())
]
