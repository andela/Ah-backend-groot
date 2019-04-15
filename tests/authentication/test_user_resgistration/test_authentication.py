from rest_framework.test import APITestCase
from rest_framework import status
from authors.apps.authentication.models import User
import re


class Authentication(APITestCase):

    def test_create_super_user(self):
        user = User.objects.create_superuser(username='superadmin',
                                             password='superadminpassword',
                                             email='supper@admin.com')
        self.assertEqual(user.is_staff, True)

    def test_for_new_user(self):
        data = {"user": {
                "username": "akram",
                "email": "akram@gmail.com",
                "password": "akrammukasA13"}
                }
        response = self.client.post('/api/users/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_return_str__method(self):
        self.user = User.objects.create_user(
            username="akram", email="akram@gmail.com", password='akram')
        self.assertEqual(self.user.__str__(), 'akram@gmail.com')

    def test_return_short_name__method(self):
        self.user = User.objects.create_user(
            username="akram", email="akram@gmail.com", password='akram')
        self.assertEqual('akram', self.user.get_short_name())

    def test_return_full_name__method(self):
        self.user = User.objects.create_user(
            username="akram", email="akram@gmail.com", password='akram')
        self.assertEqual('akram', self.user.get_full_name)

    def test_for_missing_username(self):
        """
        Method for testing if there is a missing username during registration.
        """
        data = {"user": {"username": "", "email": "akram@gmail.com",
                         "password": "akrammukasa"}}
        response = self.client.post('/api/users/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Please input a username", str(response.data))

    def test_for_missing_email(self):
        """
        Method for testing if there is a missing email during registration.
        """
        data = {"user": {
                "username": "mukasa",
                "email": "",
                "password": "akrammukasa"}}
        response = self.client.post('/api/users/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Please enter a valid email address", str(response.data))

    def test_login(self):
        data = {"user": {
                "username": "akram6",
                "email": "akram6@gmail.com",
                "password": "aKrammukasa1234"}
                }
        response = self.client.post('/api/users/', data, format='json')
        self.client.get('/api/users/verify/?token=' + response.data['token'])
        login_data = {"user": {"email": "akram6@gmail.com", "password":
                               "aKrammukasa1234"}}
        login_response = self.client.post(
            '/api/users/login/', login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get().email, "akram6@gmail.com")

    def test_login_with_non_existing_user(self):
        data = {"user": {"email": "akram@gmail.com", "password":
                         "akrammukasa"}}
        response = self.client.post('/api/users/login/', data, format='json')
        feedback = "Please signup and check for an activation link in your\
                 email"
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(re.sub(' +', ' ', feedback),
                      response.data["errors"]["error"][0])

    def test_retrieve_user_details(self):
        data = {"user": {
                "username": "akram",
                "email": "akram@gmail.com",
                "password": "aKrammukasa1234"}
                }
        response = self.client.post('/api/users/', data, format='json')
        login_data = {"user": {"email": "akram@gmail.com", "password":
                               "aKrammukasa1234"}}
        self.client.get('/api/users/verify/?token=' + response.data['token'])

        login_response = self.client.post('/api/users/login/', login_data,
                                          format='json')
        token = login_response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get('/api/user/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_updating_user_details(self):
        data = {"user": {
                "username": "akram",
                "email": "akram@gmail.com",
                "password": "aKrammukasa1234"}
                }
        response = self.client.post('/api/users/', data, format='json')
        login_data = {"user": {"email": "akram@gmail.com", "password":
                               "aKrammukasa1234"}}

        self.client.get('/api/users/verify/?token=' + response.data['token'])
        login_response = self.client.post('/api/users/login/', login_data,
                                          format='json')
        token = login_response.data["token"]

        new_data = {"user": {"email": "akram@gmail.com", "password":
                             "aKrammukasa123456789"}}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.put('/api/user/', new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
