from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied, ValidationError

from apps.accounts.models import UserProfile
from apps.accounts.services import (
    create_managed_user,
    update_managed_user,
    set_managed_user_active,
)

User = get_user_model()


class CreateManagedUserTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin_group = Group.objects.create(name="Administradores")

        cls.warehouse_group = Group.objects.create(name="Almaceneros")

        Group.objects.create(name="Consultas")

        content_type = ContentType.objects.get_for_model(UserProfile)

        permission = Permission.objects.get(
            content_type=content_type,
            codename="manage_users",
        )

        cls.admin_group.permissions.add(permission)

        cls.admin = User.objects.create_user(
            username="admin_test",
            password="AdminTest2026!Secure",
        )

        cls.admin.groups.add(cls.admin_group)

    def test_create_user_successfully(self):
        user = create_managed_user(
            username="warehouse_test",
            password="Warehouse2026!Secure",
            role="Almaceneros",
            created_by=self.admin,
            first_name="Carlos",
            last_name="Pérez",
            email="carlos@example.com",
        )

        self.assertTrue(User.objects.filter(username="warehouse_test").exists())

        self.assertTrue(user.check_password("Warehouse2026!Secure"))

        self.assertTrue(user.groups.filter(name="Almaceneros").exists())

        profile = UserProfile.objects.get(user=user)

        self.assertTrue(profile.must_change_password)

        self.assertEqual(
            profile.created_by,
            self.admin,
        )

    def test_invalid_role_is_rejected(self):
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            create_managed_user(
                username="invalid_role_user",
                password="Password2026!Secure",
                role="Superadministradores",
                created_by=self.admin,
            )

        self.assertFalse(User.objects.filter(username="invalid_role_user").exists())


class UpdateManagedUserTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin_group = Group.objects.create(name="Administradores")
        cls.warehouse_group = Group.objects.create(name="Almaceneros")
        cls.consultation_group = Group.objects.create(name="Consultas")

        permission = Permission.objects.get(
            content_type=ContentType.objects.get_for_model(UserProfile),
            codename="manage_users",
        )
        cls.admin_group.permissions.add(permission)

        cls.admin = User.objects.create_user(
            username="admin_update",
            password="AdminTest2026!Secure",
        )
        cls.admin.groups.add(cls.admin_group)

        cls.warehouse_user = User.objects.create_user(
            username="warehouse_update",
            password="Warehouse2026!Secure",
            first_name="Carlos",
            email="old@example.com",
        )
        cls.warehouse_user.groups.add(cls.warehouse_group)

    def test_update_user_and_role(self):
        updated_user = update_managed_user(
            target_user_id=self.warehouse_user.pk,
            updated_by=self.admin,
            first_name="Pedro",
            last_name="García",
            email="new@example.com",
            role="Consultas",
        )

        updated_user.refresh_from_db()

        self.assertEqual(updated_user.first_name, "Pedro")
        self.assertEqual(updated_user.last_name, "García")
        self.assertEqual(updated_user.email, "new@example.com")

        self.assertTrue(updated_user.groups.filter(name="Consultas").exists())

        self.assertFalse(updated_user.groups.filter(name="Almaceneros").exists())

    def test_cannot_edit_superuser(self):
        superuser = User.objects.create_superuser(
            username="super_update",
            email="super@example.com",
            password="SuperTest2026!Secure",
        )

        with self.assertRaises(PermissionDenied):
            update_managed_user(
                target_user_id=superuser.pk,
                updated_by=self.admin,
                first_name="Nuevo",
                last_name="Nombre",
                email="new@example.com",
                role="Consultas",
            )

    def test_cannot_edit_own_account(self):
        with self.assertRaises(PermissionDenied):
            update_managed_user(
                target_user_id=self.admin.pk,
                updated_by=self.admin,
                first_name="Nuevo",
                last_name="Nombre",
                email="new@example.com",
                role="Consultas",
            )

    def test_cannot_demote_last_active_admin(self):
        superuser = User.objects.create_superuser(
            username="super_manager",
            email="supermanager@example.com",
            password="SuperManager2026!Secure",
        )

        with self.assertRaises(ValidationError):
            update_managed_user(
                target_user_id=self.admin.pk,
                updated_by=superuser,
                first_name="Administrador",
                last_name="Principal",
                email="admin@example.com",
                role="Consultas",
            )

        self.assertTrue(self.admin.groups.filter(name="Administradores").exists())


class SetManagedUserActiveTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin_group = Group.objects.create(name="Administradores")
        cls.warehouse_group = Group.objects.create(name="Almaceneros")

        permission = Permission.objects.get(
            content_type=ContentType.objects.get_for_model(UserProfile),
            codename="manage_users",
        )
        cls.admin_group.permissions.add(permission)

        cls.admin = User.objects.create_user(
            username="admin_active",
            password="AdminTest2026!Secure",
        )
        cls.admin.groups.add(cls.admin_group)

        cls.warehouse_user = User.objects.create_user(
            username="warehouse_active",
            password="Warehouse2026!Secure",
        )
        cls.warehouse_user.groups.add(cls.warehouse_group)

    def test_deactivate_user(self):
        set_managed_user_active(
            target_user_id=self.warehouse_user.pk,
            updated_by=self.admin,
            is_active=False,
        )

        self.warehouse_user.refresh_from_db()

        self.assertFalse(self.warehouse_user.is_active)

    def test_reactivate_user(self):
        self.warehouse_user.is_active = False
        self.warehouse_user.save(update_fields=["is_active"])

        set_managed_user_active(
            target_user_id=self.warehouse_user.pk,
            updated_by=self.admin,
            is_active=True,
        )

        self.warehouse_user.refresh_from_db()

        self.assertTrue(self.warehouse_user.is_active)

    def test_cannot_deactivate_superuser(self):
        superuser = User.objects.create_superuser(
            username="super_active",
            email="super@example.com",
            password="SuperTest2026!Secure",
        )

        with self.assertRaises(PermissionDenied):
            set_managed_user_active(
                target_user_id=superuser.pk,
                updated_by=self.admin,
                is_active=False,
            )

    def test_cannot_deactivate_own_account(self):
        with self.assertRaises(PermissionDenied):
            set_managed_user_active(
                target_user_id=self.admin.pk,
                updated_by=self.admin,
                is_active=False,
            )

    def test_cannot_deactivate_last_active_admin(self):
        superuser = User.objects.create_superuser(
            username="super_manager_active",
            email="supermanager@example.com",
            password="SuperManager2026!Secure",
        )

        with self.assertRaises(ValidationError):
            set_managed_user_active(
                target_user_id=self.admin.pk,
                updated_by=superuser,
                is_active=False,
            )

        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_user_without_permission_cannot_deactivate(self):
        with self.assertRaises(PermissionDenied):
            set_managed_user_active(
                target_user_id=self.admin.pk,
                updated_by=self.warehouse_user,
                is_active=False,
            )
