from rest_framework import status
from rest_framework.test import APITestCase


class TestValidation(APITestCase):

    def setUp(self):
        self.user_one = {
            "user": {
                "username": "micheal",
                "email": "micheal@gmail.com",
                "password": "A1234567a"
            }
        }
        self.short_username = {
            "user": {
                "username": "m",
                "email": "micheal@gmail.com",
                "password": "A1234567a"
            }
        }
        self.user_one_bad_username = {
            "user": {
                "username": "+msshjbsjhbs",
                "email": "micheal@gmail.com",
                "password": "A1234567a"
            }
        }
        self.user_one_short_password = {
            "user": {
                "username": "micheal",
                "email": "micheal@gmail.com",
                "password": "A123456"
            }
        }
        self.user_one_wrong_email = {
            "user": {
                "username": "micheal",
                "email": "micheal.com",
                "password": "A1234567a"
            }
        }
        self.user_one_no_alpha = {
            "user": {
                "username": "micheal",
                "email": "micheal@gmail.com",
                "password": "12345678"
            }
        }
        self.user_one_same_user = {
            "user": {
                "username": "micheal",
                "email": "micheal@gmail.com",
                "password": "A1234567a"
            }
        }

    def test_short_username(self):
        response = self.client.post('/api/users/',
                                    self.short_username,
                                    format='json')
        data = response.data
        self.assertEqual(
            data['errors']
            ['username'], "Please the username should be atleast 4 characters")

    def test_bad_username(self):
        response = self.client.post(
            '/api/users/', self.user_one_bad_username, format='json')
        data = response.data
        self.assertEqual(
            data['errors']
            ['username'],
            "Username should start with letters")

    def test_existing_user_email(self):
        self.client.post('/api/users/', self.user_one, format='json')
        response = self.client.post(
            '/api/users/', self.user_one_same_user, format='json')
        data = response.data
        self.assertEqual(data['errors']['email'][0],
                         'user with this email already exists.')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_email(self):
        response = self.client.post(
            '/api/users/', self.user_one_wrong_email, format='json')
        data = response.data
        self.assertEqual(data["errors"]["Email"],
                         'Please enter a valid email address')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_of_length_less_than_8(self):
        response = self.client.post(
            '/api/users/', self.user_one_short_password, format='json')
        data = response.data
        self.assertEqual(
            data["errors"]
            ["password"],
            "Password should contain atleast 8 characters uppercase, number")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_not_being_alphanumeric(self):
        response = self.client.post('/api/users/',
                                    self.user_one_short_password,
                                    format='json')
        data = response.data
        self.assertEqual(
            data["errors"]
            ["password"],
            "Password should contain atleast 8 characters uppercase, number")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
