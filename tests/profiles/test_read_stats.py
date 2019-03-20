from rest_framework import status
from ..test_base import BaseTest
from tests.articles.test_category import TestCategory


class TestRateArticle(BaseTest, TestCategory):

    def test_read_stats_of_your_own_article(self):
        data = self.create_an_article(
            self.new_article,
            self.registration_data)
        token = self.register_and_login(self.another_user_data)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token.data['token'])
        self.client.get('/api/articles/{}/'.
                        format(data.data['slug']),
                        format="json")
        response = self.client.get('/api/profile/{}/read_stats/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error_message'],
                         'You cannot access this route')

    def test_read_stats_of_an_article(self):
        data = self.create_an_article(
            self.new_article,
            self.registration_data)
        token = self.register_and_login(self.another_user_data)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token.data['token'])
        self.client.get('/api/articles/{}/'.
                        format(data.data['slug']),
                        format="json")

        response = self.client.get('/api/profile/user1/read_stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
