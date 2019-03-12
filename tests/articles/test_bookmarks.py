from rest_framework import status
from .test_articles import TestArticle


class TestBookmarks(TestArticle):

    def test_can_get_bookmark(self):
        self.create_an_article(self.new_article, self.registration_data)
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get('/api/articles/me/bookmarks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_bookmark_an_article(self):
        self.create_an_article(self.new_article, self.registration_data)
        response = self.client.post(
            '/api/articles/believer/bookmark/', format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_can_bookmark_an_article_twice(self):
        self.create_an_article(self.new_article, self.registration_data)
        self.client.post(
            '/api/articles/believer/bookmark/', format="json")
        response = self.client.post(
            '/api/articles/believer/bookmark/', format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unbookmarking(self):
        self.create_an_article(self.new_article, self.registration_data)
        self.client.post(
            '/api/articles/believer/bookmark/', format="json")
        response = self.client.delete(
            '/api/articles/believer/unbookmark/', format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_can_not_bookmark_none_existing_bookmark(self):
        self.create_an_article(self.new_article, self.registration_data)
        response = self.client.delete(
            '/api/articles/believer/unbookmark/', format="json")
        self.assertIn("bookmark not found", str(response.data))
