from rest_framework import status
from ..test_base import BaseTest
from .test_category import TestCategory


class TestArticle(BaseTest, TestCategory):
    def test_return_article(self):
        self.create_an_article()
        response = self.client.get('/api/articles/')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_successful_creation_of_articles(self):
        article_response = self.create_an_article()
        self.assertEqual(article_response.status_code, status.HTTP_201_CREATED)

    def test_user_can_get_all_articles(self):
        self.create_an_article()
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_get_an_article(self):
        self.create_an_article()
        response = self.client.get('/api/article/believer/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_update_an_article(self):
        self.create_an_article()
        new_article_data = {
            "article": {
                "title": "believer",
                "description": "This test was created on womens day of 2019.",
                "body": "I like to move it move it",
            }
        }
        response = self.client.put('/api/article/believer/',
                                   data=new_article_data,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
