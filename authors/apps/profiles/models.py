from django.db import models
from authors.apps.authentication.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True)
    bio = models.CharField(max_length=255, blank=True)
    image = models.ImageField(blank=True)
    following = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    favorite_articles = models.ManyToManyField('articles.Article',
                                               related_name='favorites')

    def __str__(self):
        return self.user.username

    @receiver(post_save, sender=User)
    def create_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_profile(sender, instance, **kwargs):
        instance.profile.save()

    def favorite(self, article):
        self.favorite_articles.add(article)

    def unfavorite(self, article):
        self.favorite_articles.remove(article)

    def has_favorited(self, article):
        return self.favorite_articles.filter(pk=article.pk).exists()
