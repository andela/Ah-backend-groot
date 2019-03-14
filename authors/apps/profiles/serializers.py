from rest_framework import serializers
from .models import Profile
from ..authentication.serializers import UserSerializer
from ..authentication.models import User


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('full_name', 'bio', 'image', 'follower_count',
                  'following_count', 'timestamp', 'favorite_articles')
        read_only_fields = ('favorite_articles', )
        model = Profile

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = UserSerializer(
            instance.user,
            read_only=True).data["username"]
        return representation


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['Profile'] = ProfileSerializer(
            Profile.objects.get(user=instance),
            read_only=True).data
        return representation
