from rest_framework import serializers
from .models import Category, Article, Bookmark, Rating, Comment
from ..profiles.models import Profile
from ..profiles.serializers import ProfileSerializer
from authors.apps.authentication.models import User


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
            'average_rating',
            'user_rates',
            'created_at',
            'updated_at',
            'favorited',
            "favorites_count",
            'is_published',
            'author',
            'likes',
            'dislikes',
            'reading_time'
        )
        read_only_fields = ('id', 'slug', 'author_id', 'is_published',)
        user_rating = serializers.CharField(
            source="author.average_rating",
            required=False
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = ProfileSerializer(
            Profile.objects.get(user=instance.author),
            read_only=True).data
        representation['category'] = CategorySerializer(instance.category,
                                                        read_only=True).data
        return representation

    """Gets all the articles likes"""
    def get_likes(self, instance):
        return instance.votes.likes().count()

    """Gets all the articles dislikes"""
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


class RatingSerializer(serializers.ModelSerializer):
    """
    class holding logic for article rating
    """

    article = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all())
    rated_on = serializers.DateTimeField(read_only=True)
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all())
    score = serializers.DecimalField(required=True, max_digits=5,
                                     decimal_places=2)

    @staticmethod
    def update_data(data, slug, user: User):
        """
        method to update the article with a rating
        """
        try:
            article = Article.objects.get(slug__exact=slug)
        except Article.DoesNotExist:
            raise serializers.ValidationError("Article is not found.")

        if article.author == user:
            raise serializers.ValidationError({
                "error": [
                    "Please rate an article that does not belong to you"]
            })

        score = data.get("score", 0)
        if score > 5 or score < 0:
            raise serializers.ValidationError({
                "error": ["Score value must not go "
                          "below `0` and not go beyond `5`"]
            })

        data.update({"article": article.pk})
        data.update({"author": user.pk})
        return data

    def create(self, validated_data):
        """
        method to create and save a rating for
        """
        author = validated_data.get("author", None)
        article = validated_data.get("article", None)
        score = validated_data.get("score", 0)

        try:
            rating = Rating.objects.get(
                author=author, article__slug=article.slug)
        except Rating.DoesNotExist:
            return Rating.objects.create(**validated_data)

        rating.score = score
        rating.save()
        return rating

    class Meta:
        """
        class behaviours
        """
        model = Rating
        fields = ("score", "author", "rated_on", "article")


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            'id',
            'body',
            'created_at',
            'updated_at',
            'user',
            'article')
        read_only_fields = ('article', 'user',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = ProfileSerializer(
            Profile.objects.get(user=instance.user),
            read_only=True).data
        return representation
