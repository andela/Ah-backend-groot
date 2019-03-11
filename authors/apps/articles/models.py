from django.db import models
from .utils import get_unique_slug


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

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_unique_slug(self, 'title', 'slug')
        return super().save(*args, **kwargs)
