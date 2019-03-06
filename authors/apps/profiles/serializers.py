from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('full_name', 'bio', 'image', 'following', 'timestamp',)
        model = Profile
