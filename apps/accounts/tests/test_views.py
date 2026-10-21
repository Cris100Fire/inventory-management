from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from apps.accounts.models import UserProfile

User = get_user_model()


class UserViewsTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Crear los tres roles
        cls.admin_group = Group.objects.create(name="Administradores")
        cls.warehouse_group = Group.objects.create(name="Almaceneros")
        cls.consultation_group = Group.objects.create(name="Consultas")

        # Asignar el permiso de gestión de usuarios
        permission = Permission.objects.get(
            content_type=ContentType.objects.get_for_model(UserProfile),
            codename="manage_users",
        )
        cls.admin_group.permissions.add(permission)

        # Crear administrador
        cls.admin = User.objects.create_user(
            username="admin_views",
            password="AdminTest2026!Secure",
        )
        cls.admin.groups.add(cls.admin_group)

        # Crear almacenero
        cls.warehouse_user = User.objects.create_user(
            username="warehouse_views",
            password="Warehouse2026!Secure",
        )
        cls.warehouse_user.groups.add(cls.warehouse_group)

        # Crear usuario de consultas
        cls.consultation_user = User.objects.create_user(
            username="consultation_views",
            password="Consultation2026!Secure",
        )
        cls.consultation_user.groups.add(cls.consultation_group)

        # Crear perfiles sin cambio obligatorio pendiente
        for user in (
            cls.admin,
            cls.warehouse_user,
            cls.consultation_user,
        ):
            UserProfile.objects.get_or_create(
                user=user,
                defaults={"must_change_password": False},
            )

    def test_admin_can_access_user_list(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("accounts:user_list"))

        self.assertEqual(response.status_code, 200)

    def test_warehouse_cannot_access_user_list(self):
        self.client.force_login(self.warehouse_user)

        response = self.client.get(reverse("accounts:user_list"))

        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_redirected_to_login(self):
        response = self.client.get(reverse("accounts:user_list"))

        self.assertRedirects(
            response,
            f'{reverse("accounts:login")}?next={reverse("accounts:user_list")}',
        )

    def test_admin_can_create_user(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("accounts:user_create"),
            {
                "username": "new_warehouse",
                "first_name": "Pedro",
                "last_name": "García",
                "email": "pedro@example.com",
                "role": "Almaceneros",
                "password1": "NewWarehouse2026!Secure",
                "password2": "NewWarehouse2026!Secure",
            },
        )

        self.assertRedirects(
            response,
            reverse("accounts:user_list"),
        )

        user = User.objects.get(username="new_warehouse")

        self.assertTrue(user.groups.filter(name="Almaceneros").exists())

        profile = UserProfile.objects.get(user=user)
        self.assertTrue(profile.must_change_password)

    def test_warehouse_cannot_create_user(self):
        self.client.force_login(self.warehouse_user)

        response = self.client.post(
            reverse("accounts:user_create"),
            {
                "username": "unauthorized_user",
                "password1": "Unauthorized2026!Secure",
                "password2": "Unauthorized2026!Secure",
                "role": "Administradores",
            },
        )

        self.assertEqual(response.status_code, 403)

        self.assertFalse(User.objects.filter(username="unauthorized_user").exists())

    def test_admin_can_edit_user(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse(
                "accounts:user_update",
                args=[self.warehouse_user.pk],
            ),
            {
                "first_name": "Actualizado",
                "last_name": "Prueba",
                "email": "updated@example.com",
                "role": "Consultas",
            },
        )

        self.assertRedirects(
            response,
            reverse("accounts:user_list"),
        )

        self.warehouse_user.refresh_from_db()

        self.assertEqual(
            self.warehouse_user.first_name,
            "Actualizado",
        )

        self.assertTrue(self.warehouse_user.groups.filter(name="Consultas").exists())

    def test_cannot_edit_superuser(self):
        superuser = User.objects.create_superuser(
            username="super_views",
            email="super@example.com",
            password="SuperTest2026!Secure",
        )

        self.client.force_login(self.admin)

        response = self.client.get(
            reverse(
                "accounts:user_update",
                args=[superuser.pk],
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_admin_can_deactivate_user(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse(
                "accounts:user_toggle_active",
                args=[self.warehouse_user.pk],
            ),
            {"action": "deactivate"},
        )

        self.assertRedirects(
            response,
            reverse("accounts:user_list"),
        )

        self.warehouse_user.refresh_from_db()
        self.assertFalse(self.warehouse_user.is_active)

    def test_cannot_deactivate_using_get(self):
        self.client.force_login(self.admin)

        response = self.client.get(
            reverse(
                "accounts:user_toggle_active",
                args=[self.warehouse_user.pk],
            )
        )

        self.assertEqual(response.status_code, 405)

        self.warehouse_user.refresh_from_db()
        self.assertTrue(self.warehouse_user.is_active)

    def test_admin_can_reset_password(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse(
                "accounts:user_password_reset",
                args=[self.warehouse_user.pk],
            ),
            {
                "new_password1": "ResetPassword2026!Secure",
                "new_password2": "ResetPassword2026!Secure",
            },
        )

        self.assertRedirects(
            response,
            reverse("accounts:user_list"),
        )

        self.warehouse_user.refresh_from_db()

        self.assertTrue(self.warehouse_user.check_password("ResetPassword2026!Secure"))

        profile = UserProfile.objects.get(user=self.warehouse_user)

        self.assertTrue(profile.must_change_password)
