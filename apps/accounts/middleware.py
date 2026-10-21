from django.shortcuts import redirect
from django.conf import settings
from django.urls import resolve, Resolver404

from .models import UserProfile


class ForcePasswordChangeMiddleware:
    ALLOWED_ROUTES = {
        "accounts:change_password",
        "accounts:logout",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        if self.is_static_request(request):
            return self.get_response(request)

        if self.is_allowed_route(request):
            return self.get_response(request)

        must_change_password = UserProfile.objects.filter(
            user=request.user,
            must_change_password=True,
        ).exists()

        if must_change_password:
            return redirect("accounts:change_password")

        return self.get_response(request)

    def is_static_request(self, request):
        static_url = settings.STATIC_URL

        return bool(
            static_url
            and static_url.startswith("/")
            and request.path_info.startswith(static_url)
        )

    def is_allowed_route(self, request):
        try:
            match = resolve(request.path_info)
        except Resolver404:
            return False

        return match.view_name in self.ALLOWED_ROUTES
