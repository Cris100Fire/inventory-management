from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.accounts.models import UserProfile

User = get_user_model()


class UserProfileSignalTests(TestCase):

    def test_profile_created_automatically(self):
        user = User.objects.create_user(
            username="signal_user",
            password="Signal2026!Secure",
        )

        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_profile_not_duplicated_when_user_updated(self):
        user = User.objects.create_user(
            username="signal_update_user",
            password="Signal2026!Secure",
        )

        user.first_name = "Carlos"
        user.save(update_fields=["first_name"])

        self.assertEqual(
            UserProfile.objects.filter(user=user).count(),
            1,
        )

    def test_superuser_also_receives_profile(self):
        superuser = User.objects.create_superuser(
            username="signal_superuser",
            email="super@example.com",
            password="SuperSignal2026!Secure",
        )

        self.assertTrue(UserProfile.objects.filter(user=superuser).exists())

    def test_profile_deleted_with_user(self):
        user = User.objects.create_user(
            username="signal_delete_user",
            password="Signal2026!Secure",
        )

        user_id = user.pk
        user.delete()

        self.assertFalse(UserProfile.objects.filter(user_id=user_id).exists())
