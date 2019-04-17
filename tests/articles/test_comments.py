from rest_framework import status
from ..test_base import BaseTest
from .test_category import TestCategory


class TestComment(BaseTest, TestCategory):

    def create_comment(self):
        article_response = self.create_an_article(
            self.article, self.registration_data)
        slug = article_response.data["slug"]
        return self.client.post(
            "/api/articles/{}/comments/".format(str(slug)),
            self.comment_data, format="json"), slug

    def test_get_comment(self):
        comment_reponse, slug = self.create_comment()

        get_response = self.client.get(
            "/api/articles/{}/comments/".format(str(slug)))
        self.assertEqual(comment_reponse.status_code, status.HTTP_201_CREATED)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertIn("body", get_response.data["Comment"][0])
        comment_id = comment_reponse.data["id"]

        get_one_article = self.client.get(
            "/api/articles/{}/comments/{}/".format(str(slug), comment_id))
        self.assertEqual(get_one_article.data['id'], comment_id)
        self.assertEqual(get_one_article.status_code, status.HTTP_200_OK)

    def test_get_mulitple_comments_one_one_slug(self):
        article_response = self.create_an_article(
            self.article, self.registration_data)
        slug = article_response.data["slug"]
        self.client.post(
            "/api/articles/{}/comments/".format(str(slug)),
            self.comment_data, format="json")
        self.client.post(
            "/api/articles/{}/comments/".format(str(slug)),
            self.new_comment_data, format="json")
        response = self.client.get(
            "/api/articles/{}/comments/".format(str(slug)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comment_on_article(self):
        article_response = self.create_an_article(
            self.article, self.registration_data)
        slug = article_response.data["slug"]
        comment_reponse = self.client.post(
            "/api/articles/{}/comments/".format(str(slug)),
            self.comment_data, format="json")
        self.assertEqual(comment_reponse.status_code, status.HTTP_201_CREATED)

    def test_update_article_comment(self):
        article_response = self.create_an_article(
            self.article, self.registration_data)
        slug = article_response.data["slug"]
        post_response = self.client.post(
            "/api/articles/{}/comments/".format(str(slug)),
            self.comment_data, format="json")
        comment_id = post_response.data["id"]
        update_response = self.client.put(
            "/api/articles/{}/comments/{}/".format(str(slug), comment_id),
            self.change_comment, format="json")
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

    def test_get_comment_of_article_slug_that_doesnot_exist(self):
        self.create_an_article(
            self.article, self.registration_data)
        get_response = self.client.get("/api/articles/sbsbds/comments/")
        self.assertEqual(get_response.data["errors"][0], "No comments found")
        self.assertEqual(get_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_commenting_without_logging_in(self):
        get_response = self.client.get("/api/articles/sbsbds/comments/")
        self.assertEqual(get_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_article_comment_edit_history(self):
        article_response = self.create_an_article(
            self.article, self.registration_data)
        slug = article_response.data["slug"]
        post_response = self.client.post(
            "/api/articles/{}/comments/".format(str(slug)),
            self.comment_data, format="json")
        comment_id = post_response.data["id"]
        self.client.put(
            "/api/articles/{}/comments/{}/".format(str(slug), comment_id),
            self.change_comment, format="json")
        self.client.put(
            "/api/articles/{}/comments/{}/".format(str(slug), comment_id),
            self.change_comment, format="json")
        response = self.client.get(
            "/api/articles/{}/comments/{}/history/".format(str(slug),
                                                           comment_id),
            self.change_comment, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_not_get_edit_history_when_comment_is_not_edited(self):
        article_response = self.create_an_article(
            self.article, self.registration_data)
        slug = article_response.data["slug"]
        post_response = self.client.post(
            "/api/articles/{}/comments/".format(str(slug)),
            self.comment_data, format="json")
        comment_id = post_response.data["id"]
        response = self.client.get(
            "/api/articles/{}/comments/{}/history/".format(str(slug),
                                                           comment_id),
            self.change_comment, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_highlight_and_comment_on_any_test(self):
        article_response = self.create_an_article(
            self.article, self.registration_data)
        slug = article_response.data["slug"]
        comment_reponse = self.client.post(
            "/api/articles/{}/comments/".format(str(slug)),
            self.highlight_comment, format="json")
        self.assertEqual(comment_reponse.status_code, status.HTTP_201_CREATED)
