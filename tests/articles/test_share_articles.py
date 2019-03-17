from rest_framework import status
from ..test_base import BaseTest
from .test_category import TestCategory


class TestShareArticle(BaseTest, TestCategory):

    def test_user_can_share_an_article_on_gmail(self):
        response = self.create_an_article(
            self.new_article,
            self.registration_data)
        data = {"share_with": "stanley.okwii@andela.com"}
        response = self.client.post('/api/article/believer/share/gmail/',
                                    data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_share_an_article_on_facebook(self):
        response = self.create_an_article(
            self.new_article,
            self.registration_data)
        response = self.client.post('/api/article/believer/share/facebook/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_share_an_article_on_twitter(self):
        response = self.create_an_article(
            self.new_article,
            self.registration_data)
        response = self.client.post('/api/article/believer/share/twitter/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_not_share_an_article_with_valid_url(self):
        response = self.create_an_article(
            self.new_article,
            self.registration_data)
        response = self.client.post('/api/article/believer/share/wrongurl/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
