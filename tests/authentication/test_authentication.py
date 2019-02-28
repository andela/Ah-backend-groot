from rest_framework.test import APITestCase
from rest_framework import status
from authors.apps.authentication.models import User


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
                "password": "akrammukasa"}
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
        self.assertIn("This field may not be blank.", str(response.data))

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
        self.assertIn("This field may not be blank.", str(response.data))

    def test_login(self):
        data = {"user": {
                "username": "akram",
                "email": "akram@gmail.com",
                "password": "akrammukasa"}
                }
        response = self.client.post('/api/users/', data, format='json')

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
