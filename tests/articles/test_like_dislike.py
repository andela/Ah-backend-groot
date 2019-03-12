from rest_framework import status
from ..test_base import BaseTest
from .test_category import TestCategory


class TestLikeDislikeArticle(BaseTest, TestCategory):

    def test_liking_an_article(self):
        like_data = self.create_an_article()
        response = self.client.post('/api/articles/{}/like/'.
                                    format(like_data.data['slug']),
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('likes'), 1)

    def test_unlike_article(self):
        like_data = self.create_an_article()
        response = self.client.post('/api/articles/{}/like/'.
                                    format(like_data.data['slug']),
                                    format="json")
        self.assertEqual(response.data.get('likes'), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        unlike_response = self.client.post('/api/articles/{}/like/'.
                                           format(like_data.data['slug']),
                                           format="json")
        self.assertEqual(unlike_response.data.get('likes'), 0)
        self.assertEqual(unlike_response.status_code, status.HTTP_201_CREATED)

    def test_dislike_article(self):
        dislike_data = self.create_an_article()
        response = self.client.post('/api/articles/{}/dislike/'.
                                    format(dislike_data.data['slug']),
                                    format="json")
        self.assertEqual(response.data.get('dislikes'), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_undislike_article(self):
        dislike_data = self.create_an_article()
        response = self.client.post('/api/articles/{}/dislike/'.
                                    format(dislike_data.data['slug']),
                                    format="json")
        self.assertEqual(response.data.get('dislikes'), 1)
        second_response = self.client.post('/api/articles/{}/dislike/'.
                                           format(dislike_data.data['slug']),
                                           format="json")
        self.assertEqual(second_response.data.get('dislikes'), 0)
