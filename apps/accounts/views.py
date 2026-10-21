from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, FormView
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.db.models import Q
from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from django.views import View
from django.shortcuts import redirect
from django.http import Http404
from django.db import transaction
from typing import cast
from django.contrib.auth.base_user import AbstractBaseUser

from .forms import (
    UserRegisterForm,
    ManagedUserCreateForm,
    ManagedUserUpdateForm,
    ManagedPasswordResetForm,
    MandatoryPasswordChangeForm,
)

from .services import (
    create_managed_user,
    update_managed_user,
    ALLOWED_ROLES,
    set_managed_user_active,
    reset_managed_user_password,
)

from .models import UserProfile


class RegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Tu cuenta se creó correctamente. Ya puedes iniciar sesión.",
        )
        return super().form_valid(form)


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    pass


User = get_user_model()


class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = User
    template_name = "accounts/users/user_list.html"
    context_object_name = "users"
    permission_required = "accounts.manage_users"
    paginate_by = 20

    def get_queryset(self):
        queryset = User.objects.prefetch_related("groups").order_by("username")

        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query)
                | Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
                | Q(email__icontains=search_query)
            )

        role = self.request.GET.get("role", "")

        valid_roles = (
            "Administradores",
            "Almaceneros",
            "Consultas",
        )

        if role in valid_roles:
            queryset = queryset.filter(groups__name=role)

        status = self.request.GET.get("status", "")

        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["roles"] = Group.objects.filter(
            name__in=(
                "Administradores",
                "Almaceneros",
                "Consultas",
            )
        ).order_by("name")

        context["search_query"] = self.request.GET.get("q", "").strip()
        context["selected_role"] = self.request.GET.get("role", "")
        context["selected_status"] = self.request.GET.get("status", "")

        return context


class UserCreateView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    form_class = ManagedUserCreateForm
    template_name = "accounts/users/user_create.html"
    success_url = reverse_lazy("accounts:user_list")
    permission_required = "accounts.manage_users"

    def form_valid(self, form):
        try:
            user = create_managed_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                email=form.cleaned_data["email"],
                role=form.cleaned_data["role"],
                created_by=self.request.user,
            )
        except ValidationError as error:
            form.add_error(None, error)
            return self.form_invalid(form)

        messages.success(
            self.request,
            f"El usuario «{user.username}» se creó correctamente.",
        )

        return super().form_valid(form)


class UserUpdateView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    form_class = ManagedUserUpdateForm
    template_name = "accounts/users/user_update.html"
    success_url = reverse_lazy("accounts:user_list")
    permission_required = "accounts.manage_users"

    def get_target_user(self):
        return get_object_or_404(
            User,
            pk=self.kwargs["pk"],
        )

    def dispatch(self, request, *args, **kwargs):
        self.target_user = self.get_target_user()

        if self.target_user.is_superuser or self.target_user.pk == request.user.pk:
            if request.user.is_authenticated:
                raise PermissionDenied("No puedes editar esta cuenta.")

        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()

        initial.update(
            {
                "first_name": self.target_user.first_name,
                "last_name": self.target_user.last_name,
                "email": self.target_user.email,
                "role": (
                    self.target_user.groups.filter(name__in=ALLOWED_ROLES)
                    .values_list("name", flat=True)
                    .first()
                ),
            }
        )

        return initial

    def form_valid(self, form):
        try:
            user = update_managed_user(
                target_user_id=self.target_user.pk,
                updated_by=self.request.user,
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                email=form.cleaned_data["email"],
                role=form.cleaned_data["role"],
            )
        except ValidationError as error:
            form.add_error(None, error)
            return self.form_invalid(form)

        messages.success(
            self.request,
            f"El usuario «{user.username}» se actualizó correctamente.",
        )

        return super().form_valid(form)


class UserToggleActiveView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "accounts.manage_users"

    def post(self, request, pk):
        action = request.POST.get("action")

        if action not in ("activate", "deactivate"):
            messages.error(
                request,
                "La acción solicitada no es válida.",
            )
            return redirect("accounts:user_list")

        try:
            updated_user = set_managed_user_active(
                target_user_id=pk,
                updated_by=request.user,
                is_active=(action == "activate"),
            )
        except User.DoesNotExist:
            raise Http404("El usuario no existe.")
        except ValidationError as error:
            messages.error(
                request,
                " ".join(error.messages),
            )
            return redirect("accounts:user_list")

        status = "activado" if updated_user.is_active else "desactivado"

        messages.success(
            request,
            f"El usuario «{updated_user.username}» fue {status} correctamente.",
        )

        return redirect("accounts:user_list")


class UserPasswordResetView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    form_class = ManagedPasswordResetForm
    template_name = "accounts/users/user_reset_password.html"
    success_url = reverse_lazy("accounts:user_list")
    permission_required = "accounts.manage_users"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.target_user = get_object_or_404(
                User,
                pk=kwargs["pk"],
            )

            if self.target_user.is_superuser or self.target_user.pk == request.user.pk:
                raise PermissionDenied(
                    "No puedes restablecer la contraseña de esta cuenta."
                )

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            user = reset_managed_user_password(
                target_user_id=self.target_user.pk,
                updated_by=self.request.user,
                new_password=form.cleaned_data["new_password1"],
            )

        except ValidationError as error:
            form.add_error(
                "new_password1",
                error,
            )
            return self.form_invalid(form)

        messages.success(
            self.request,
            f"Se restableció la contraseña de «{user.username}». "
            "Deberá cambiarla al iniciar sesión.",
        )

        return super().form_valid(form)


class MandatoryPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "accounts/change_password.html"
    form_class = MandatoryPasswordChangeForm
    success_url = reverse_lazy("dashboard:home")

    def form_valid(self, form):
        with transaction.atomic():
            form.save()

            UserProfile.objects.update_or_create(
                user=self.request.user,
                defaults={
                    "must_change_password": False,
                },
            )

        authenticated_user = cast(
            AbstractBaseUser,
            self.request.user,
        )

        update_session_auth_hash(
            self.request,
            authenticated_user,
        )

        messages.success(
            self.request,
            "Tu contraseña se actualizó correctamente.",
        )

        return redirect(self.get_success_url())
