from ..test_base import BaseTest
from rest_framework import status


class TestProfile(BaseTest):

    def test_create_profile(self):
        response = super().register_and_login()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_does_not_exist(self):
        response = self.client.get('/api/profiles/someone/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_update_profile(self):
        response = super().register_and_login()
        token = response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.put("/api/profiles/user/",
                                   self.update_data, format="json")
        self.client.put('/api/profiles/user/update/',
                        self.update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_update_profile(self):
        response = self.client.put('/api/profiles/user/',
                                   self.update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
