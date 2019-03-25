from django.shortcuts import get_object_or_404
from rest_framework.generics import (UpdateAPIView,
                                     RetrieveUpdateAPIView,
                                     ListAPIView)
from .models import Notification
from authors.apps.profiles.models import Subscription
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import SubscriptionSerializer, NotificationSerializer
from rest_framework import status


class ListNotificationView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def list(self, request, *args, **kwargs):
        user = request.user
        instance = self.queryset.filter(recipients=user.profile)
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data)


class NotificationView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        Notification.objects.filter(pk=self.kwargs.get('id')).update(read=True)
        instance = Notification.objects.filter(pk=self.kwargs.get('id'))[0]
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class SubscriptionView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(), user=self.request.user)

    def update(self, request, *args, **kwargs):
        notify_type = self.kwargs['type']
        subscription = self.get_object()
        if(notify_type == 'email'):
            subscription.email_notifications = True
            message = 'emails'
        elif(notify_type == 'in_app'):
            message = 'in app notifications'
            subscription.in_app_notifications = True
        else:
            return Response(
                {'message': "bad request"},
                status=status.HTTP_400_BAD_REQUEST)
        subscription.save()

        return Response({'message': "You have subscribe \
            to {}".format(message)}, status=status.HTTP_200_OK)
