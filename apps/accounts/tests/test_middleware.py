from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from apps.accounts.models import UserProfile

User = get_user_model()


class ForcePasswordChangeMiddlewareTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.group = Group.objects.create(name="Consultas")

        cls.user = User.objects.create_user(
            username="middleware_user",
            password="Temporary2026!Secure",
        )

        cls.user.groups.add(cls.group)

        cls.profile = UserProfile.objects.create(
            user=cls.user,
            must_change_password=True,
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_dashboard_redirects_when_password_change_required(self):
        response = self.client.get(reverse("dashboard:home"))

        self.assertRedirects(
            response,
            reverse("accounts:change_password"),
            fetch_redirect_response=False,
        )

    def test_catalog_redirects_when_password_change_required(self):
        response = self.client.get("/catalog/")

        self.assertRedirects(
            response,
            reverse("accounts:change_password"),
            fetch_redirect_response=False,
        )

    def test_admin_redirects_when_password_change_required(self):
        response = self.client.get("/admin/")

        self.assertRedirects(
            response,
            reverse("accounts:change_password"),
            fetch_redirect_response=False,
        )

    def test_password_change_page_is_accessible(self):
        response = self.client.get(reverse("accounts:change_password"))

        self.assertEqual(response.status_code, 200)

    def test_logout_is_allowed(self):
        response = self.client.post(reverse("accounts:logout"))

        self.assertEqual(response.status_code, 302)

        self.assertNotIn(
            "_auth_user_id",
            self.client.session,
        )

    def test_cannot_reuse_current_password(self):
        response = self.client.post(
            reverse("accounts:change_password"),
            {
                "old_password": "Temporary2026!Secure",
                "new_password1": "Temporary2026!Secure",
                "new_password2": "Temporary2026!Secure",
            },
        )

        self.assertEqual(response.status_code, 200)

        form = response.context["form"]

        self.assertIn(
            "new_password1",
            form.errors,
        )

        self.assertIn(
            "La nueva contraseña debe ser diferente de tu contraseña actual.",
            form.errors["new_password1"],
        )

        self.profile.refresh_from_db()

        self.assertTrue(self.profile.must_change_password)

        self.user.refresh_from_db()

        self.assertTrue(self.user.check_password("Temporary2026!Secure"))

    def test_successful_password_change(self):
        response = self.client.post(
            reverse("accounts:change_password"),
            {
                "old_password": "Temporary2026!Secure",
                "new_password1": "NewPersonal2026!Secure",
                "new_password2": "NewPersonal2026!Secure",
            },
        )

        self.assertRedirects(
            response,
            reverse("dashboard:home"),
        )

        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertTrue(self.user.check_password("NewPersonal2026!Secure"))

        self.assertFalse(self.profile.must_change_password)

    def test_dashboard_access_after_password_change(self):
        self.profile.must_change_password = False
        self.profile.save(update_fields=["must_change_password"])

        response = self.client.get(reverse("dashboard:home"))

        self.assertEqual(response.status_code, 200)

    def test_password_change_keeps_session_active(self):
        response = self.client.post(
            reverse("accounts:change_password"),
            {
                "old_password": "Temporary2026!Secure",
                "new_password1": "NewPersonal2026!Secure",
                "new_password2": "NewPersonal2026!Secure",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.assertIn(
            "_auth_user_id",
            self.client.session,
        )
