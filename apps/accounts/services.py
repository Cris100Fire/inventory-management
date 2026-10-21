from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.core.exceptions import PermissionDenied, ValidationError

from .models import UserProfile

User = get_user_model()

ALLOWED_ROLES = (
    "Administradores",
    "Almaceneros",
    "Consultas",
)


@transaction.atomic
def create_managed_user(
    *, username, password, role, created_by, first_name="", last_name="", email=""
):
    if not created_by.is_active or not created_by.has_perm("accounts.manage_users"):
        raise ValidationError("No tienes permiso para crear usuarios")

    if role not in ALLOWED_ROLES:
        raise ValidationError("El rol seleccionado no es válido.")

    try:
        gruop = Group.objects.get(name=role)
    except Group.DoesNotExist:
        raise ValidationError("El grupo seleccionado no está configurado.")

    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        email=email,
    )

    user.groups.add(gruop)

    UserProfile.objects.update_or_create(
        user=user,
        defaults={
            "must_change_password": True,
            "created_by": created_by,
        },
    )

    return user


def is_active_inventory_admin(user):
    return (
        user.is_active
        and user.groups.filter(name="Administradores").exists()
        and user.has_perm("accounts.manage_users")
    )


def lock_administrator_role():
    return Group.objects.select_for_update().get(name="Administradores")


@transaction.atomic
def update_managed_user(
    *,
    target_user_id,
    updated_by,
    first_name,
    last_name,
    email,
    role,
):
    if not updated_by.is_active or not updated_by.has_perm("accounts.manage_users"):
        raise PermissionDenied("No tienes permiso para editar usuarios")

    if role not in ALLOWED_ROLES:
        raise ValidationError("El rol seleccionado no es válido")

    lock_administrator_role()

    target = User.objects.select_for_update().get(pk=target_user_id)

    if target.is_superuser:
        raise PermissionDenied("No puedes modificar superusuarios desde este módulo.")

    if target.pk == updated_by.pk:
        raise PermissionDenied("No puedes modificar tu propia cuenta.")

    try:
        group = Group.objects.get(name=role)
    except Group.DoesNotExist:
        raise ValidationError("El grupo seleccionado no está configurado.")

    if (
        target.groups.filter(name="Administradores").exists()
        and role != "Administradores"
    ):
        other_admin_exist = (
            User.objects.filter(is_active=True, groups__name="Administradores")
            .exclude(pk=target.pk)
            .exists()
        )

        if not other_admin_exist:
            raise ValidationError(
                "No puedes cambiar el rol de un administrador activo."
            )

    target.first_name = first_name
    target.last_name = last_name
    target.email = email

    target.save(
        update_fields=[
            "first_name",
            "last_name",
            "email",
        ]
    )

    target.groups.set([group])

    return target


@transaction.atomic
def set_managed_user_active(
    *,
    target_user_id,
    updated_by,
    is_active,
):
    if not updated_by.is_active or not updated_by.has_perm("accounts.manage_users"):
        raise PermissionDenied("No tienes permiso para gestionar usuarios.")

    lock_administrator_role()

    target = User.objects.select_for_update().get(pk=target_user_id)

    if target.is_superuser:
        raise PermissionDenied("No puedes modificar el estado de un superusuario.")

    if target.pk == updated_by.pk:
        raise PermissionDenied("No puedes activar o desactivar tu propia cuenta.")

    if target.is_active == is_active:
        return target

    if not is_active and target.groups.filter(name="Administradores").exists():
        other_admins_exist = (
            User.objects.filter(
                is_active=True,
                groups__name="Administradores",
            )
            .exclude(pk=target.pk)
            .exists()
        )

        if not other_admins_exist:
            raise ValidationError(
                "No puedes desactivar al último administrador activo."
            )

    target.is_active = is_active
    target.save(update_fields=["is_active"])

    return target


@transaction.atomic
def reset_managed_user_password(
    *,
    target_user_id,
    updated_by,
    new_password,
):
    if not updated_by.is_active or not updated_by.has_perm("accounts.manage_users"):
        raise PermissionDenied("No tienes permiso para restablecer contraseñas.")

    target = User.objects.select_for_update().get(pk=target_user_id)

    if target.is_superuser:
        raise PermissionDenied(
            "No puedes restablecer la contraseña de un superusuario."
        )

    if target.pk == updated_by.pk:
        raise PermissionDenied(
            "No puedes restablecer tu propia contraseña desde este módulo."
        )

    if target.check_password(new_password):
        raise ValidationError(
            "La nueva contraseña debe ser diferente "
            "de la contraseña actual del usuario."
        )

    validate_password(new_password, user=target)

    profile, _ = UserProfile.objects.get_or_create(user=target)

    target.set_password(new_password)
    target.save(update_fields=["password"])

    profile.must_change_password = True
    profile.save(update_fields=["must_change_password", "updated_at"])

    return target
