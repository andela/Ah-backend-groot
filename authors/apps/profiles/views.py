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
from .renderers import ProfileJSONRenderer, ReadingStatsJSONRenderer
from .permissions import IsOwnerOrReadOnly
from .serializers import ProfileSerializer
from authors.apps.articles.serializers import ReadStatsSerializer
from .models import Profile
from authors.apps.articles.models import ReadingStats
from authors.apps.authentication.models import User
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

    def get_profile(self, *args, **kwargs):
        profile = Profile.objects.get(
            user__username=self.kwargs.get('username')
        )
        return profile


class FollowersListView(FollowersFollowingView):
    def get_queryset(self, *args, **kwargs):
        return self.get_profile().followed_by.all()


class FollowingListView(FollowersFollowingView):
    def get_queryset(self, *args, **kwargs):
        return self.get_profile().follows.all()


class ReadingStatsView(ListAPIView):
    """
    class view that reurns a list of articles read by one user
    """
    serializer_class = ReadStatsSerializer
    permission_classes = (IsAuthenticated,)
    renderer_classes = [ReadingStatsJSONRenderer, ]

    def get_queryset(self, *args, **kwargs):

        username = self.kwargs.get('username')
        author = get_object_or_404(User, username=username)
        read_stats = ReadingStats.objects.all().filter(user=author)
        return [item.article for item in read_stats]

    def get(self, request, username):
        list_of_articles = -20
        if username == request.user.username:
            articles = self.get_queryset()
            list_of_articles = [{'title': article.title,
                                 'slug': article.slug,
                                 'author': article.author.username}
                                for article in articles[list_of_articles:]]
            data = {
                'user': request.user.username,
                'No_of_Read_articles': len(articles),
                'Most_recent_articles': list(reversed(list_of_articles))
            }
            return Response(data)
        else:
            return Response({
                'error_message': 'You cannot access this route'
            }, status=status.HTTP_403_FORBIDDEN)
