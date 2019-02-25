from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from authors.apps.authentication.models import User


class Authentication(APITestCase):

    def test_for_new_user(self):
        # url = reverse('signup')
        data = {"user": {"username": "akram",
                         "email": "akram@gmail.com", "password":
                         "akrammukasa"}}
        response = self.client.post('/api/users/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_for_missing_username(self):
        """
        Method for testing if there is a missing username during registration.
        """
        data = {"user": {"username": "", "email": "akram@gmail.com",
                "password": "akrammukasa"}}
        response = self.client.post('/api/users/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This field may not be blank.", str(response.data))

    def test_for_missing_email(self):
        """
        Method for testing if there is a missing email during registration.
        """
        data = {"user": {"username": "mukasa", "email": "", "password":
                "akrammukasa"}}
        response = self.client.post('/api/users/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This field may not be blank.", str(response.data))

    def test_login(self):
        # url = reverse('signup')
        data = {"user": {"username": "akram",
                         "email": "akram@gmail.com", "password":
                         "akrammukasa"}}
        response = self.client.post('/api/users/', data, format='json')
        # url = reverse('login')
        data = {"user": {"email": "akram@gmail.com", "password":
                "akrammukasa"}}
        response = self.client.post('/api/users/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get().email, "akram@gmail.com")

    def test_login_with_non_existing_user(self):
        data = {"user": {"email": "akram@gmail.com", "password":
                         "akrammukasa"}}
        response = self.client.post('/api/users/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("A user with this email and password was not found.", 
                      str(response.data))
