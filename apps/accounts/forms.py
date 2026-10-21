from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm

from .services import ALLOWED_ROLES


class UserRegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)


User = get_user_model()


class ManagedUserCreateForm(UserCreationForm):
    first_name = forms.CharField(
        label="Nombre",
        max_length=150,
        required=False,
    )

    last_name = forms.CharField(
        label="Apellido",
        max_length=150,
        required=False,
    )

    email = forms.EmailField(
        label="Correo electrónico",
        required=False,
    )

    role = forms.ChoiceField(
        label="Rol",
        choices=[(role, role) for role in ALLOWED_ROLES],
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
        )


class ManagedUserUpdateForm(forms.Form):
    first_name = forms.CharField(
        label="Nombre",
        max_length=150,
        required=False,
    )

    last_name = forms.CharField(
        label="Apellido",
        max_length=150,
        required=False,
    )

    email = forms.EmailField(
        label="Correo electrónico",
        required=False,
    )

    role = forms.ChoiceField(
        label="Rol",
        choices=[(role, role) for role in ALLOWED_ROLES],
    )


class ManagedPasswordResetForm(forms.Form):
    new_password1 = forms.CharField(
        label="Nueva contraseña temporal",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    new_password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def clean(self):
        cleaned_data = super().clean()

        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if not password1 or not password2:
            return cleaned_data

        if password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return cleaned_data


class MandatoryPasswordChangeForm(PasswordChangeForm):
    def clean_new_password1(self):
        new_password = self.cleaned_data.get("new_password1")

        if new_password and self.user.check_password(new_password):
            raise forms.ValidationError(
                "La nueva contraseña debe ser diferente de tu contraseña actual.",
                code="password_unchanged",
            )

        return new_password
