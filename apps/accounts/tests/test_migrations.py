from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class UserProfileMigrationTests(TransactionTestCase):

    migrate_from = [
        ("accounts", "0003_alter_userprofile_options"),
    ]

    migrate_to = [
        ("accounts", "0004_backfill_user_profiles"),
    ]

    def setUp(self):
        super().setUp()

        self.executor = MigrationExecutor(connection)

        # Regresar al estado anterior a la migración.
        self.executor.migrate(self.migrate_from)

        old_apps = self.executor.loader.project_state(self.migrate_from).apps

        User = old_apps.get_model("auth", "User")
        UserProfile = old_apps.get_model(
            "accounts",
            "UserProfile",
        )

        # Crear un usuario antiguo.
        self.user = User.objects.create(
            username="legacy_user",
            password="legacy_password_hash",
            is_active=True,
        )

        # Los modelos históricos no registran nuestras
        # señales actuales: podemos simular un perfil faltante.
        self.assertFalse(UserProfile.objects.filter(user_id=self.user.pk).exists())

        # Aplicar la migración que queremos probar.
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_to)

        self.apps = self.executor.loader.project_state(self.migrate_to).apps

    def tearDown(self):
        # Restaurar el esquema al estado más reciente.
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())

        super().tearDown()

    def test_migration_creates_missing_profile(self):
        UserProfile = self.apps.get_model(
            "accounts",
            "UserProfile",
        )

        self.assertTrue(UserProfile.objects.filter(user_id=self.user.pk).exists())

    def test_migration_preserves_user_data(self):
        User = self.apps.get_model("auth", "User")

        user_data = User.objects.values(
            "username",
            "password",
            "is_active",
        ).get(pk=self.user.pk)

        self.assertEqual(
            user_data["username"],
            "legacy_user",
        )

        self.assertEqual(
            user_data["password"],
            "legacy_password_hash",
        )

        self.assertTrue(user_data["is_active"])

    def test_migration_uses_safe_profile_defaults(self):
        UserProfile = self.apps.get_model(
            "accounts",
            "UserProfile",
        )

        profile_data = UserProfile.objects.values(
            "must_change_password",
            "created_by_id",
        ).get(user_id=self.user.pk)

        self.assertFalse(profile_data["must_change_password"])

        self.assertIsNone(profile_data["created_by_id"])
