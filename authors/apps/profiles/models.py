from django.db import models
from authors.apps.authentication.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Subscription(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="notification_subscription"
    )
    email_notifications = models.BooleanField(default=False)
    in_app_notifications = models.BooleanField(default=False)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True)
    bio = models.CharField(max_length=255, blank=True)
    image = models.URLField(blank=True)
    follows = models.ManyToManyField(
        'self',
        related_name='followed_by',
        symmetrical=False
    )
    follower_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    favorite_articles = models.ManyToManyField('articles.Article',
                                               related_name='favorites')

    def __str__(self):
        return self.user.username

    def follow(self, profile):
        self.follows.add(profile)

    def unfollow(self, profile):
        self.follows.remove(profile)

    def is_followed_by(self, profile):
        """
        This method updates the "following" boolean field
        depending on if the user retrieving the profile
        follows the current user or not
        """
        self.following = self.followed_by.filter(pk=profile.pk).exists()
        return self.following

    def favorite(self, article):
        self.favorite_articles.add(article)

    def unfavorite(self, article):
        self.favorite_articles.remove(article)

    def has_favorited(self, article):
        return self.favorite_articles.filter(pk=article.pk).exists()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        Subscription.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
