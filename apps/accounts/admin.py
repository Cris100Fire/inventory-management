from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "must_change_password",
        "created_by",
        "created_at",
    )

    list_filter = ("must_change_password",)
    search_fields = ("user__username", "user__email")

    readonly_fields = (
        "created_at",
        "updated_at",
    )
