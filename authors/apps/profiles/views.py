from rest_framework.generics import (
    ListAPIView,
    RetrieveUpdateAPIView,
    CreateAPIView,
    DestroyAPIView
)
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    AllowAny
)
from .renderers import ProfileJSONRenderer
from .permissions import IsOwnerOrReadOnly
from .serializers import ProfileSerializer
from .models import Profile
from rest_framework import status, serializers
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
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
        AllowAny,)
    renderer_classes = (ProfileJSONRenderer,)

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(), user__username=self.kwargs.get('username'))

    def retrieve(self, request, *args, **kwargs):
        profile = self.get_object()
        follower = self.request.user.profile
        serializer_data = request.data.get('profile', {})
        serializer_data.update(user=request.user)
        serializer = self.serializer_class(
            profile, data=serializer_data, partial=True
        )
        serializer.is_valid()
        following = str(profile.is_followed_by(follower))
        data = serializer.data
        data.update({"following": following})
        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        profile = self.get_object()
        self.check_object_permissions(self.request, profile)
        serializer_data = request.data.get('profile', {})
        serializer_data.update(user=request.user)
        serializer = self.serializer_class(
            request.user.profile, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowProfileView(CreateAPIView, DestroyAPIView):
    queryset = Profile.objects.all()
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(), user__username=self.kwargs.get('username'))

    def delete(self, request, username=None):
        profile = self.get_object()
        follower = self.request.user.profile
        follower.unfollow(profile)
        follower_count = follower.follower_count
        following_count = profile.following_count
        follower.follower_count = follower_count - 1
        profile.following_count = following_count - 1
        follower.save()
        profile.save()
        serializer = self.serializer_class(profile, context={
            'request': request
        })
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

    def post(self, request, username=None):
        profile = self.get_object()
        follower = self.request.user.profile
        if follower.pk is profile.pk:
            raise serializers.ValidationError('You can not follow yourself')
        if profile.is_followed_by(follower):
            raise serializers.ValidationError('You already follow this user')
        follower.follow(profile)
        follower_count = follower.follower_count
        following_count = profile.following_count
        follower.follower_count = follower_count + 1
        profile.following_count = following_count + 1
        follower.save()
        profile.save()
        serializer = self.serializer_class(profile, context={
            'request': request
        })
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FollowersFollowingView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer


class FollowersListView(FollowersFollowingView):
    def get_queryset(self, *args, **kwargs):
        profile = Profile.objects.get(
            user__username=self.kwargs.get('username')
        )
        return profile.followed_by.all()


class FollowingListView(FollowersFollowingView):
    def get_queryset(self, *args, **kwargs):
        profile = Profile.objects.get(
            user__username=self.kwargs.get('username')
        )
        return profile.follows.all()
