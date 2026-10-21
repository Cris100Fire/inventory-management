import threading
from queue import Queue

from django.contrib.auth.models import Group
from django.db import (
    connections,
    transaction,
)
from django.test import TransactionTestCase

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.accounts.services import set_managed_user_active, update_managed_user


class AdministratorLockConcurrencyTests(TransactionTestCase):

    databases = {"default"}

    def setUp(self):
        self.group = Group.objects.create(name="Administradores")

    def test_second_transaction_waits_for_lock(self):
        """
        Comprueba que dos conexiones distintas
        no pueden adquirir simultáneamente
        el bloqueo del grupo Administradores.
        """

        first_locked = threading.Event()
        release_first = threading.Event()
        second_attempting = threading.Event()
        second_acquired = threading.Event()

        errors = Queue()

        def first_transaction():
            try:
                with transaction.atomic():
                    Group.objects.select_for_update().get(pk=self.group.pk)

                    first_locked.set()

                    if not release_first.wait(timeout=10):
                        raise TimeoutError("La primera transacción no fue liberada.")

            except Exception as exc:
                errors.put(exc)
            finally:
                first_locked.set()
                connections.close_all()

        def second_transaction():
            try:
                if not first_locked.wait(timeout=10):
                    raise TimeoutError("La primera transacción no obtuvo el bloqueo.")

                with transaction.atomic():
                    second_attempting.set()

                    Group.objects.select_for_update().get(pk=self.group.pk)

                    second_acquired.set()

            except Exception as exc:
                errors.put(exc)
            finally:
                connections.close_all()

        thread_a = threading.Thread(target=first_transaction)

        thread_b = threading.Thread(target=second_transaction)

        thread_a.start()

        try:
            self.assertTrue(
                first_locked.wait(timeout=10),
                "La primera transacción no comenzó.",
            )

            thread_b.start()

            self.assertTrue(
                second_attempting.wait(timeout=10),
                "La segunda transacción no comenzó.",
            )

            # Mientras A mantiene el bloqueo,
            # B no debe haberlo adquirido.
            self.assertFalse(
                second_acquired.wait(timeout=0.3),
                "La segunda transacción adquirió " "un bloqueo que seguía ocupado.",
            )

        finally:
            release_first.set()

            thread_a.join(timeout=10)

            if thread_b.ident is not None:
                thread_b.join(timeout=10)

        self.assertFalse(
            thread_a.is_alive(),
            "La primera transacción no terminó.",
        )

        self.assertFalse(
            thread_b.is_alive(),
            "La segunda transacción no terminó.",
        )

        self.assertTrue(
            errors.empty(),
            f"Errores de concurrencia: {list(errors.queue)}",
        )

        self.assertTrue(
            second_acquired.is_set(),
            "La segunda transacción nunca obtuvo el bloqueo.",
        )


User = get_user_model()


class AdministratorServiceConcurrencyTests(TransactionTestCase):

    databases = {"default"}

    def setUp(self):
        self.admin_group = Group.objects.create(name="Administradores")

        self.manager = User.objects.create_superuser(
            username="concurrency_manager",
            email="manager@example.com",
            password="Manager2026!Secure",
        )

        self.admin_a = User.objects.create_user(
            username="admin_concurrency_a",
            password="AdminA2026!Secure",
        )
        self.admin_a.groups.add(self.admin_group)

        self.admin_b = User.objects.create_user(
            username="admin_concurrency_b",
            password="AdminB2026!Secure",
        )
        self.admin_b.groups.add(self.admin_group)

    def deactivate_admin(self, user_id, barrier):
        """
        Ejecuta el servicio desde una conexión
        independiente de MySQL.
        """
        connections.close_all()

        try:
            barrier.wait(timeout=10)

            set_managed_user_active(
                target_user_id=user_id,
                updated_by=self.manager,
                is_active=False,
            )

            return "success"

        except ValidationError:
            return "rejected"

        finally:
            connections.close_all()

    def test_concurrent_deactivation_preserves_one_admin(self):
        barrier = Barrier(2)

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_a = executor.submit(
                self.deactivate_admin,
                self.admin_a.pk,
                barrier,
            )

            future_b = executor.submit(
                self.deactivate_admin,
                self.admin_b.pk,
                barrier,
            )

            results = [
                future_a.result(timeout=20),
                future_b.result(timeout=20),
            ]

        self.assertCountEqual(
            results,
            ["success", "rejected"],
        )

        active_admins = User.objects.filter(
            groups__name="Administradores",
            is_active=True,
            is_superuser=False,
        ).count()

        self.assertEqual(active_admins, 1)

    def demote_admin(self, user_id, barrier):
        """
        Intenta cambiar el rol de un administrador
        desde una conexión independiente.
        """
        connections.close_all()

        try:
            barrier.wait(timeout=10)

            update_managed_user(
                target_user_id=user_id,
                updated_by=self.manager,
                first_name="Administrador",
                last_name="Actualizado",
                email="updated@example.com",
                role="Consultas",
            )

            return "success"

        except ValidationError:
            return "rejected"

        finally:
            connections.close_all()

    def test_concurrent_deactivation_and_demotion(self):
        """
        Una desactivación y una degradación simultáneas
        no deben dejar cero administradores activos.
        """
        Group.objects.get_or_create(name="Consultas")

        barrier = Barrier(2)

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_deactivation = executor.submit(
                self.deactivate_admin,
                self.admin_a.pk,
                barrier,
            )

            future_demotion = executor.submit(
                self.demote_admin,
                self.admin_b.pk,
                barrier,
            )

            results = [
                future_deactivation.result(timeout=20),
                future_demotion.result(timeout=20),
            ]

        self.assertCountEqual(
            results,
            ["success", "rejected"],
        )

        active_admins = (
            User.objects.filter(
                groups__name="Administradores",
                is_active=True,
                is_superuser=False,
            )
            .distinct()
            .count()
        )

        self.assertEqual(active_admins, 1)

        self.admin_a.refresh_from_db()
        self.admin_b.refresh_from_db()

        admin_a_still_active = (
            self.admin_a.is_active
            and self.admin_a.groups.filter(name="Administradores").exists()
        )

        admin_b_still_active = (
            self.admin_b.is_active
            and self.admin_b.groups.filter(name="Administradores").exists()
        )

        self.assertNotEqual(
            admin_a_still_active,
            admin_b_still_active,
        )
