from rest_framework import status
from ..test_base import BaseTest
from .test_category import TestCategory


class TestLikeDislikeArticle(BaseTest, TestCategory):

    def test_liking_an_article(self):
        like_data = self.create_an_article(
            self.new_article,
            self.registration_data)
        response = self.client.post('/api/articles/{}/like/'.
                                    format(like_data.data['slug']),
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('likes'), 1)

    def test_unlike_article(self):
        like_data = self.create_an_article(
            self.new_article,
            self.registration_data)
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
        dislike_data = self.create_an_article(
            self.new_article,
            self.registration_data)
        response = self.client.post('/api/articles/{}/dislike/'.
                                    format(dislike_data.data['slug']),
                                    format="json")
        self.assertEqual(response.data.get('dislikes'), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_undislike_article(self):
        dislike_data = self.create_an_article(
            self.new_article,
            self.registration_data)
        response = self.client.post('/api/articles/{}/dislike/'.
                                    format(dislike_data.data['slug']),
                                    format="json")
        self.assertEqual(response.data.get('dislikes'), 1)
        second_response = self.client.post('/api/articles/{}/dislike/'.
                                           format(dislike_data.data['slug']),
                                           format="json")
        self.assertEqual(second_response.data.get('dislikes'), 0)

    def test_like_a_comment(self):
        article_response = self.create_an_article(
            self.new_article,
            self.registration_data)
        slug = article_response.data["slug"]
        comment_response = self.client.post(
            "/api/articles/{}/comments/".format(str(slug)),
            self.comment_data, format="json")
        id = comment_response.data["id"]
        response = self.client.post('/api/articles/{}/comments/{}/like/'.
                                    format(str(slug), id),
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('likes'), 1)
