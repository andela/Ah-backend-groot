from django.db import models
from .utils import get_unique_slug
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from authors.apps.authentication.models import User


class LikeDislikeManager(models.Manager):
    # Gets all the votes greater than 0. In this case they're likes.
    def likes(self):
        return self.get_queryset().filter(vote__gt=0)

    # Gets all the votes less than 0. In this case they're dislikes.
    def dislikes(self):
        return self.get_queryset().filter(vote__lt=0)


class LikeDislike(models.Model):
    """Likes and Dislikes model."""
    LIKE = 1
    DISLIKE = -1

    VOTES = ((DISLIKE, 'Dislike'), (LIKE, 'Like'))

    vote = models.SmallIntegerField(choices=VOTES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    objects = LikeDislikeManager()


class Category(models.Model):
    slug = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_unique_slug(self, 'name', 'slug')
        return super().save(*args, **kwargs)


class Article(models.Model):
    slug = models.SlugField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    favorited = models.BooleanField(default=False)
    favorites_count = models.IntegerField(default=0)
    image = models.URLField(blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    category = models.ForeignKey(
        'articles.Category',
        to_field='slug',
        on_delete=models.CASCADE,
        related_name='articles_category',
    )
    author = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='author_articles'
    )
    votes = GenericRelation(LikeDislike, related_name='articles')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_unique_slug(self, 'title', 'slug')
        return super().save(*args, **kwargs)
