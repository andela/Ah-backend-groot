from rest_framework import status
from ..test_base import BaseTest
from .test_category import TestCategory


class TestRateArticle(BaseTest, TestCategory):

    def test_rate_an_article(self):
        rate_data = self.create_an_article(
            self.new_article,
            self.registration_data)
        rating = {"article": {"score": 1}}
        token = self.register_and_login(self.another_user_data)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token.data['token'])
        response = self.client.post('/api/article/{}/rate/'.
                                    format(rate_data.data['slug']),
                                    data=rating,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rate_no_an_article(self):
        rate_data = self.registration_data
        rating = {"article": {"score": 1}}
        token = self.register_and_login(self.another_user_data)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token.data['token'])
        response = self.client.post('/api/article/{}/rate/'.
                                    format(rate_data),
                                    data=rating,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'][0],
                         'Article is not found.')

    def test_rate_out_of_range_an_article(self):
        rate_data = self.create_an_article(
            self.new_article,
            self.registration_data)
        rating = {"article": {"score": 7}}
        token = self.register_and_login(self.another_user_data)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token.data['token'])
        response = self.client.post('/api/article/{}/rate/'.
                                    format(rate_data.data['slug']),
                                    data=rating,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors']['error'][0],
                         "Score value must not go "
                         "below `0` and not go beyond `5`")

    def test_rating_your_article(self):
        rate_data = self.create_an_article(
            self.new_article,
            self.registration_data)
        rating = {"article": {"score": 2}}
        response = self.client.post('/api/article/{}/rate/'.
                                    format(rate_data.data['slug']),
                                    data=rating,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors']['error'][0],
                         "Please rate an article that does not belong to you")

    def test_already_rated_an_article(self):
        rate_data = self.create_an_article(
            self.new_article,
            self.registration_data)
        rating = {"article": {"score": 1}}
        token = self.register_and_login(self.another_user_data)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token.data['token'])
        self.client.post('/api/article/{}/rate/'.
                         format(rate_data.data['slug']),
                         data=rating,
                         format="json")
        rating = {"article": {"score": 2}}
        response = self.client.post('/api/article/{}/rate/'.
                                    format(rate_data.data['slug']),
                                    data=rating,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
