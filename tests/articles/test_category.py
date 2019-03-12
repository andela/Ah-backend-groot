
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from authors.apps.authentication.models import User


class TestCategory(APITestCase):

    def setUp(self):
        self.super_user = {'username': 'superadmin',
                           'password': 'superadminpassword',
                           'email': 'supper@admin.com'}
        self.client = APIClient()

    def create_super_user(self):
        User.objects.create_superuser(username="superadmin",
                                      password="superadminpassword",
                                      email="supper@admin.com")

    def get_admin_token(self):
        self.create_super_user()
        login_data = {"user": {"email": "supper@admin.com",
                      "password": "superadminpassword"}}
        response = self.client.post(
            '/api/users/login/', login_data, format='json')
        return response.data["token"]

    def add_category(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.get_admin_token())
        return self.client.post("/api/categories/",
                                data=({
                                    "category": {
                                        "name": "Religion"}}
                                      ),
                                format='json')

    def test_can_get_categories(self):
        self.add_category()
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_add_category(self):
        response = self.add_category()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_can_update_category(self):
        self.add_category()
        response = self.client.put("/api/categories/religion",
                                   data=({"name": "Science"}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_delete_category(self):
        self.add_category()
        response = self.client.delete("/api/categories/religion")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_can_view_user_profile(self):
        self.add_category()
        response = self.client.get("/api/users/list/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
