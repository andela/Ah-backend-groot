from rest_framework import status
from rest_framework.test import APITestCase, APIClient


class TestRegistration(APITestCase):

    def registering_with_no_data(self):
        data = {}
        response = self.client.post('/api/users/', data, format='json')
        self.assertEqual(response.data["errors"]["input fields"],
                         "Please provide a username, email address \
                          and a password")
        self.assertEqual(response.status, status.HTTP_400_BAD_REQUEST)

    def test_recieve_a_token_after_registration(self):
        data = {
            "user": {
                "username": "user",
                "email": "users@gmail.com",
                "password": "Users@2011"
            }
        }
        response = self.client.post('/api/users/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        assert 'token' in response.data

    def test_token_received_after_successful_login(self):
        """
        Test that a user will receive
        a token after successfull login
        """
        data = {
            "user": {
                "username": "users",
                "email": "userstest@gmail.com",
                "password": "Users@2011"
            }
        }
        registration_response = self.client.post('/api/users/', data,
                                                 format='json')
        registration_token = registration_response.data['token']
        self.client.post('/api/users/verify/?token=' + registration_token,
                         format='json')
        login_data = {
            "user": {
                "email": "userstest@gmail.com",
                "password": "Users@2011"}
        }
        response = self.client.post('/api/users/login/',
                                    login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert 'token' in response.data

    def test_unsuccessfull_registration_without_use_name(self):
        data = {"user": {
                "username": "",
                "email": "users@gmail.com",
                "password": "users@2011"}
                }
        response = self.client.post('/api/users/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_token_prefix_in_header(self):
        """
        Test when wrong authoriation header
        prefix is entered
        """
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='token name' + 'token key')
        response = client.get("/api/user/", format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authentication_with_invalid_user(self):
        """
        Test authentication with invalid users
        """
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer' + 'token key')
        response = client.get("/api/user/", format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authentication_with_wrong_token_authorization(self):
        """
        Test authentication with invalid users
        """
        self.client.credentials(HTTP_AUTHORIZATION='ggghghgh' + 'nhjnhjjhhj')
        response = self.client.get("/api/user/", format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unsuccessfull_registration_without_user_name_field(self):
        data = {"user": {
                "email": "users@gmail.com",
                "password": "Users@2011"}
                }
        response = self.client.post('/api/users/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsuccessfull_wrong_token(self):
        client = APIClient()
        token_key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9. \
            eyJpZCI6MywiZXhwIjoxNTU2NTM4MTgxfQ.sIF_X-yPMENo1T \
            vTPPj2NHbEW-dYERK4CXdJnbkhb0Adsk'
        client.credentials(HTTP_AUTHORIZATION='Bearer' + token_key)
        response = client.get("/api/user/", format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_no_authorization_header_in_request(self):
        """
        Test when no authorization header in the request
        """
        client = APIClient()
        # client.credentials(HTTP_AUTHORIZATION= ' ' + 'token')
        response = client.get("/api/user/", format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_verification_email_is_sent(self):
        data = {
            "user": {
                "username": "user",
                "email": "users@gmail.com",
                "password": "Users@2011"
            }
        }
        registration_response = self.client.post('/api/users/',
                                                 data, format='json')
        token = registration_response.data["token"]
        response = self.client.post('/api/users/verify/?token=' + token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
