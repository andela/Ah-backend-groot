from django.db import models
from django.db.models.signals import post_save
from authors.apps.articles.models import Article, Comment
from ..profiles.models import Profile
from django.dispatch import receiver
from django.db.models import Q
from .utils import send_emails_to_recipients
import re


class Notification(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    recipients = models.ManyToManyField(to=Profile,
                                        related_name='notifications',
                                        related_query_name='notification')
    time_stamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)


@receiver(post_save, sender=Article)
def article_handler(sender, instance, **kwargs):
    if instance.is_published:
        profile_list = instance.author.profile.followed_by.all()

        subscribed_users = profile_list.filter(
            Q(user__notification_subscription__in_app_notifications=True) | Q(
                user__notification_subscription__email_notifications=True))

        email_subscribed_users = profile_list.filter(
            user__notification_subscription__email_notifications=True)
        if(subscribed_users.count() >= 1):

            notification = Notification.objects.create(
                title="New Article on Authors Heaven",
                body=re.sub('  +', ' ', "{} has published another article \
                                                titled {}".format(
                    instance.author.username.capitalize(),
                    instance.title)))
            notification.recipients.add(*subscribed_users)

            if(email_subscribed_users.count() >= 1):
                send_emails_to_recipients(notification, email_subscribed_users)

            notification.save()


@receiver(post_save, sender=Comment)
def comment_handler(sender, instance, **kwargs):
    profile_list = Profile.objects.all()
    users_who_favorited_article = profile_list.filter(
        favorite_articles=instance.article.pk)
    subscribed_users = users_who_favorited_article.filter(
        Q(user__notification_subscription__in_app_notifications=True) | Q(
            user__notification_subscription__email_notifications=True))
    email_subscribed_users = users_who_favorited_article.filter(
        user__notification_subscription__email_notifications=True)
    if(subscribed_users.count() >= 1):

        notification = Notification.objects.create(
            title="New Comment on article that you favorited.",
            body=re.sub('  +', ' ', "The article titled {} that you \
             favorited has a new comment '{}' by {}"
                        .format(instance.article.title,
                                instance.article.body,
                                instance.user.username)))
        notification.recipients.add(*subscribed_users)

        if(email_subscribed_users.count() >= 1):
            send_emails_to_recipients(notification, email_subscribed_users)

        notification.save()
