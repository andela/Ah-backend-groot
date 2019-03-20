from rest_framework import status
from ..test_base import BaseTest
from .test_category import TestCategory


class TestRateArticle(BaseTest, TestCategory):

    def test_report_an_article(self):
        report_data = self.create_an_article(
            self.new_article,
            self.registration_data)
        report = {"reported_reason": "The article is a nonsense"}
        token = self.register_and_login(self.another_user_data)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token.data['token'])
        response = self.client.post('/api/article/{}/report/'.
                                    format(report_data.data['slug']),
                                    data=report,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_already_reported_article(self):
        report_data = self.create_an_article(
            self.new_article,
            self.registration_data)
        report = {"reported_reason": "The article is a nonsense"}
        token = self.register_and_login(self.another_user_data)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token.data['token'])
        self.client.post('/api/article/{}/report/'.
                         format(report_data.data['slug']),
                         data=report,
                         format="json")
        report = {"reported_reason": "The article is above age"}
        response = self.client.post('/api/article/{}/report/'.
                                    format(report_data.data['slug']),
                                    data=report,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'],
                         "You have already reported this Article")

    def test_report_an_article_that_doesnot_exit(self):
        report_data = self.create_an_article(
            self.empty_article,
            self.registration_data)
        report = {"reported_reason": "The article is a nonsense"}
        token = self.register_and_login(self.another_user_data)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token.data['token'])
        response = self.client.post('/api/article/{}/report/'.
                                    format(report_data.data),
                                    data=report,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'],
                         "Article does not exist!")
