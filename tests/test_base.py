from rest_framework.test import APITestCase, APIClient


class BaseTest(APITestCase):

    def setUp(self):
        self.update_data = {
            "full_name": "User Full Name",
            "bio": "This is my bio"
        }
        self.registration_data = {
            "user": {
                "username": "user",
                "email": "userstest@gmail.com",
                "password": "Users@12345"
            }
        }
        self.login_data = {
            "user": {
                "email": "userstest@gmail.com",
                "password": "Users@12345"
            }
        }
        self.new_article = {
            "article": {
                "title": "believer",
                "description": "This test was created on womens day of 2019.",
                "body": "I like to move it move it, I like to move it",
            }
        }
        self.client = APIClient()

    def register_and_login(self):
        response = self.client.post('/api/users/',
                                    self.registration_data, format='json')
        self.client.post(
            '/api/users/verify/?token=' + response.data["token"])
        login_response = self.client.post('/api/users/login/',
                                          self.login_data, format='json')
        return login_response

    def create_an_article(self):
        new_category = self.add_category()
        token = self.register_and_login()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token.data['token'])
        self.new_article['article']['category'] = new_category.data['slug']
        response = self.client.post('/api/articles/',
                                    self.new_article,
                                    format='json')
        return response
