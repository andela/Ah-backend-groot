from rest_framework import status
from ..test_base import BaseTest
from .test_category import TestCategory


class TestArticle(BaseTest, TestCategory):
    def test_return_article(self):
        response = self.create_an_article(
            self.new_article,
            self.registration_data)
        response = self.client.get('/api/articles/')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_successful_creation_of_articles(self):
        article_response = self.create_an_article(
            self.new_article,
            self.registration_data)
        self.assertEqual(article_response.status_code, status.HTTP_201_CREATED)

    def test_user_can_get_all_articles(self):
        response = self.create_an_article(
            self.new_article,
            self.registration_data)
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_get_an_article(self):
        response = self.create_an_article(
            self.new_article,
            self.registration_data)
        response = self.client.get('/api/article/believer/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_update_an_article(self):
        response = self.create_an_article(
            self.new_article,
            self.registration_data)
        response = self.client.put('/api/article/believer/',
                                   data=self.new_article_data,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_favorite_article(self):
        article_1 = self.create_an_article(self.new_article,
                                           self.registration_data)

        token = self.register_and_login(self.another_user_data).data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.post("/api/article/{0}/favorite/".format(
            article_1.data['slug']
        ), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_can_not_favorite_own_article(self):
        article_1 = self.create_an_article(self.new_article,
                                           self.registration_data)
        response = self.client.post("/api/article/{0}/favorite/".format(
            article_1.data['slug']
        ), format="json")
        message = "can not favorite own article"
        self.assertEqual(response.data['message'], message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_not_favorite_own_article_again(self):
        article_1 = self.create_an_article(self.new_article,
                                           self.registration_data)
        token = self.register_and_login(self.another_user_data).data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.client.post("/api/article/{0}/favorite/".format(
            article_1.data['slug']
        ), format="json")
        response = self.client.post("/api/article/{0}/favorite/".format(
            article_1.data['slug']
        ), format="json")
        message = "article can not be favorited again"
        self.assertEqual(response.data['message'], message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_un_favorite_article(self):
        article_1 = self.create_an_article(self.new_article,
                                           self.registration_data)

        token = self.register_and_login(self.another_user_data).data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.client.post("/api/article/{0}/favorite/".format(
            article_1.data['slug']
        ), format="json")
        response = self.client.delete("/api/article/{0}/unfavorite/".format(
            article_1.data['slug']
        ), format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_can_not_un_favorite_article_before_favoriting_it(self):
        article_1 = self.create_an_article(self.new_article,
                                           self.registration_data)

        token = self.register_and_login(self.another_user_data).data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.delete("/api/article/{0}/unfavorite/".format(
            article_1.data['slug']
        ), format="json")

        response_message = "This article is not in your favorite list"
        self.assertEqual(response.data['message'], response_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
