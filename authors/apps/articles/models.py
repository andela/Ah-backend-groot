from django.db import models
from .utils import get_unique_slug
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from authors.apps.authentication.models import User
from django.utils import timezone
from django.db.models import Avg
from django.conf import settings
import math


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
    is_published = models.BooleanField(default=False)
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
    tags = models.ManyToManyField(
        'articles.Tag',
        related_name='articles'
    )
    votes = GenericRelation(LikeDislike, related_name='articles')
    user_rates = models.CharField(max_length=10, default=0)
    reading_time = models.CharField(null=True, max_length=100)
    read_stats = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_unique_slug(self, 'title', 'slug')
            self.reading_time = self.calculate_reading_time()
        return super().save(*args, **kwargs)

    @property
    def average_rating(self):
        """
        method to calculate the average rating of the article.
        """
        ratings = self.scores.all().aggregate(score=Avg("score"))
        return float('%.2f' % (ratings["score"] if ratings['score'] else 0))

    def calculate_reading_time(self):
        word_count = 0
        for word in self.body:
            word_count += len(word) / settings.WORD_LENGTH
        result = math.ceil(word_count / settings.WORD_PER_MINUTE)
        return str(result) + " min read"

    class Meta:
        get_latest_by = 'created_at'
        ordering = ['-created_at', 'author']


class Bookmark(models.Model):
    user = models.ForeignKey(User, blank=False, on_delete=models.CASCADE)
    slug = models.ForeignKey(Article, blank=False, on_delete=models.CASCADE,
                             to_field='slug')
    bookmarked_at = models.DateTimeField(
        auto_created=True, auto_now=False, default=timezone.now)


class Rating(models.Model):
    """
        Model for rating an article
    """
    article = models.ForeignKey(Article, related_name="scores",
                                on_delete=models.CASCADE)
    author = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name="scores",
        null=True)
    rated_on = models.DateTimeField(auto_now_add=True)
    score = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ["-score"]


class Comment(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE
    )
    article = models.ForeignKey(
        'Article', on_delete=models.CASCADE, to_field="slug", blank=False
    )
    body = models.TextField(max_length=500)
    article_section = models.TextField(blank=True, null=True)
    start_position = models.CharField(max_length=500, blank=True, null=True)
    end_position = models.CharField(max_length=500, blank=True, null=True)


class CommentHistory(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    body = models.TextField()
    updated_at = models.DateTimeField(auto_now_add=True)


class Tag(models.Model):
    tag = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(db_index=True, unique=True)

    def __str__(self):
        return self.tag

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_unique_slug(self, 'tag', 'slug')
        return super().save(*args, **kwargs)


class ReportedArticle(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    reported_at = models.DateTimeField(auto_now_add=True)
    reported_reason = models.CharField(max_length=500, blank=False)

    def __str__(self):
        return self.reported_reason

    class Meta:
        ordering = ['-reported_at']


class ReadingStats(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE,
                                blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read_stats = models.IntegerField(default=0)

    def __str__(self):
        return "article_title: {}, user: {}, read_stats: {}".format(
            self.article,
            self.user,
            self.read_stats)
