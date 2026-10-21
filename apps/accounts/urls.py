from django.urls import path

from .views import (
    UserLoginView,
    UserLogoutView,
    UserListView,
    UserCreateView,
    UserUpdateView,
    UserToggleActiveView,
    UserPasswordResetView,
    MandatoryPasswordChangeView,
)

app_name = "accounts"

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/create/", UserCreateView.as_view(), name="user_create"),
    path("users/<int:pk>/edit/", UserUpdateView.as_view(), name="user_update"),
    path(
        "users/<int:pk>/toggle-active/",
        UserToggleActiveView.as_view(),
        name="user_toggle_active",
    ),
    path(
        "users/<int:pk>/reset-password/",
        UserPasswordResetView.as_view(),
        name="user_password_reset",
    ),
    path(
        "change-password/",
        MandatoryPasswordChangeView.as_view(),
        name="change_password",
    ),
]
