from rest_framework import serializers
from .models import Profile
from authors.apps.authentication.serializers import UserSerializer


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('full_name', 'bio', 'image', 'timestamp',)
        model = Profile

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = UserSerializer(
            instance.user,
            read_only=True).data["email"]
        return representation
