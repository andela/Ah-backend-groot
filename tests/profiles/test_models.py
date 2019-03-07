from .test_base import BaseTest
from authors.apps.profiles.models import Profile


class TestProfile(BaseTest):

    def test_return_profile(self):
        super().register_and_login()
        profile = Profile.objects.latest('id')
        self.assertTrue(profile)
