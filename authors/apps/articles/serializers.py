from rest_framework import serializers
from .models import Category, Article, Bookmark
from ..profiles.serializers import ProfileSerializer
from ..profiles.models import Profile


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'name',
            'slug',
            'id')
        read_only_fields = ('id', 'slug',)


class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            'slug',
            'title',
            'description',
            'body',
            'category',
            'created_at',
            'updated_at',
            'favorited',
            "favorites_count",
            'is_published',
            'author',
            'likes',
            'dislikes'
        )
        read_only_fields = ('id', 'slug', 'author_id', 'is_published',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = ProfileSerializer(
            Profile.objects.get(user=instance.author),
            read_only=True).data
        representation['category'] = CategorySerializer(instance.category,
                                                        read_only=True).data
        return representation

    def get_likes(self, instance):
        return instance.votes.likes().count()

    def get_dislikes(self, instance):
        return instance.votes.dislikes().count()


class BookmarkSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='slug.author.username')
    slug = serializers.ReadOnlyField(source='slug.slug')
    image = serializers.ReadOnlyField(source='slug.image')
    article_title = serializers.ReadOnlyField(source='slug.title')
    description = serializers.ReadOnlyField(source='slug.title')

    class Meta:
        model = Bookmark
        fields = ['author', 'article_title', 'slug',
                  'description', 'bookmarked_at', 'image']
