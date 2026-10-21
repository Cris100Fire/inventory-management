from django.urls import path

from .views import (
    StockMovementListView,
    StockMovementDetailView,
    StockMovementCreateView,
)

app_name = "inventory"

urlpatterns = [
    path("movements/", StockMovementListView.as_view(), name="movement_list"),
    path(
        "movements/create/",
        StockMovementCreateView.as_view(),
        name="movement_create",
    ),
    path(
        "movements/<int:pk>/",
        StockMovementDetailView.as_view(),
        name="movement_detail",
    ),
]
