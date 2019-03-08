from rest_framework.test import APITestCase


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

        self.registration_follow_data = {
            "user": {
                "username": "user1",
                "email": "userstest1@gmail.com",
                "password": "Users@12345"
            }
        }

    def register_and_login(self):
        response = self.client.post('/api/users/',
                                    self.registration_data, format='json')
        self.client.post(
            '/api/users/verify/?token=' + response.data["token"])
        login_response = self.client.post('/api/users/login/',
                                          self.login_data, format='json')
        return login_response

    def register_follow_user(self):
        response = self.client.post('/api/users/',
                                    self.registration_follow_data,
                                    format='json')
        return response
