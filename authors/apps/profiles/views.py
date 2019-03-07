from rest_framework.generics import (
    ListAPIView,
    RetrieveUpdateAPIView)
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    AllowAny
)
from .renderers import ProfileJSONRenderer
from .permissions import IsOwnerOrReadOnly
from .serializers import ProfileSerializer
from .models import Profile
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class ListProfileView(ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    ordering_fields = ('timestamp')


class RetrieveUpdateProfileView(RetrieveUpdateAPIView):
    """
    This class allows a user to view a profile
    and only its owner to edit it
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly, AllowAny,)
    renderer_classes = (ProfileJSONRenderer,)

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(), user__username=self.kwargs.get('username'))

    def update(self, request, *args, **kwargs):
        profile = self.get_object()
        self.check_object_permissions(self.request, profile)
        serializer_data = request.data.get('profile', {})
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
