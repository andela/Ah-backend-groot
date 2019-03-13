from rest_framework import serializers
from .models import Profile
from authors.apps.authentication.serializers import UserSerializer


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
