from tests.test_base import BaseTest
from rest_framework import status


class TestProfile(BaseTest):

    def test_create_profile(self):
        response = super().register_and_login(self.registration_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_does_not_exist(self):
        response = self.client.get('/api/profiles/someone/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_profile(self):
        response = super().register_and_login(self.registration_data)
        token = response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get("/api/profiles/user/",
                                   format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_update_profile(self):
        response = super().register_and_login(self.registration_data)
        token = response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.put("/api/profiles/user/",
                                   self.update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_update_profile(self):
        response = self.client.put('/api/profiles/user/',
                                   self.update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_follow_user(self):
        response1 = super().register_and_login(self.registration_data)
        super().register_follow_user()
        token1 = response1.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token1)
        response = self.client.post("/api/profiles/user1/follow/",
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_authenticated_unfollow_user(self):
        response1 = super().register_and_login(self.registration_data)
        super().register_follow_user()
        token1 = response1.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token1)
        response = self.client.delete("/api/profiles/user1/follow/",
                                      format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_authenticated_follow_themself(self):
        response1 = super().register_and_login(self.registration_data)
        token1 = response1.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token1)
        response = self.client.post("/api/profiles/user/follow/",
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_followers(self):
        response1 = super().register_and_login(self.registration_data)
        super().register_follow_user()
        token1 = response1.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token1)
        response = self.client.get("/api/profiles/user1/followers/",
                                   format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_following(self):
        response1 = super().register_and_login(self.registration_data)
        super().register_follow_user()
        token1 = response1.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token1)
        response = self.client.get("/api/profiles/user1/following/",
                                   format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
