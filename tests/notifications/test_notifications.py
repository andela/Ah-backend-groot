from tests.test_base import BaseTest
from rest_framework import status
from ..articles.test_category import TestCategory
import re


class TestNotification(BaseTest, TestCategory):

    def test_receiving_notifications_when_article_is_published(self):
        user_two = self.register_and_login(self.another_user_data)
        author = self.register_and_login(self.registration_data)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + user_two.data['token'])
        self.client.post('/api/profiles/user/follow/')
        self.subscribe_user_for_email_notifications(user_two.data['token'])
        self.subscribe_user_for_in_app_notifications(user_two.data['token'])
        self.add_article(author.data.get('token'), self.article)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + author.data['token'])
        self.client.post('/api/article/believer/publish/')
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + user_two.data['token'])
        get_notififications = self.client.get('/api/notifications/')
        self.assertEqual(get_notififications.status_code, status.HTTP_200_OK)
        body = "User has published another article titled believer"
        self.assertEqual(get_notififications.data[0]["body"],
                         body)

    def test_receiving_notifications_when_favorite_article_gets_comment(self):
        comment_data = {"comment": {
            "body": "This is a great story"
        }}
        user_two = self.register_and_login(self.another_user_data)
        author = self.register_and_login(self.registration_data)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + user_two.data['token'])
        self.subscribe_user_for_email_notifications(user_two.data['token'])
        self.subscribe_user_for_in_app_notifications(user_two.data['token'])
        self.add_article(author.data.get('token'), self.article)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + author.data['token'])
        self.client.post('/api/article/believer/publish/')
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + user_two.data['token'])
        self.client.post('/api/article/believer/favorite/')
        user_three = self.register_and_login(self.third_user_data)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + user_three.data['token'])
        self.client.post('/api/articles/believer/comments/',
                         comment_data, format="json")

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + user_two.data['token'])
        get_notififications = self.client.get('/api/notifications/')
        self.assertEqual(get_notififications.status_code, status.HTTP_200_OK)
        title = "New Comment on article that you favorited."
        body = re.sub('  +', ' ', "The article titled believer that you favorited has a new\
             comment 'I like to move it move it, I like to move it' by user3")
        self.assertEqual(get_notififications.data[0]["title"], title)
        self.assertEqual(get_notififications.data[0]["body"], body)

    def test_marking_notification_as_read(self):
        user_two = self.register_and_login(self.another_user_data)
        author = self.register_and_login(self.registration_data)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + user_two.data['token'])
        self.client.post('/api/profiles/user/follow/')
        self.subscribe_user_for_email_notifications(user_two.data['token'])
        self.subscribe_user_for_in_app_notifications(user_two.data['token'])
        self.add_article(author.data.get('token'), self.article)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + author.data['token'])
        self.client.post('/api/article/believer/publish/')
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + user_two.data['token'])
        get_one_notification = self.client.put('/api/notifications/1/')
        self.assertEqual(get_one_notification.data["read"], True)
