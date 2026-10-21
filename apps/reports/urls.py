from django.urls import path

from .views import (
    StockReportView,
    StockReportExportView,
    LowStockReportView,
    LowStockReportExportView,
    MovementReportView,
    MovementReportExportView,
)

app_name = "reports"

urlpatterns = [
    path("stock/", StockReportView.as_view(), name="stock_report"),
    path(
        "stock/export/<str:export_format>/",
        StockReportExportView.as_view(),
        name="stock_export",
    ),
    path(
        "low-stock/",
        LowStockReportView.as_view(),
        name="low_stock_report",
    ),
    path(
        "low-stock/export/<str:export_format>/",
        LowStockReportExportView.as_view(),
        name="low_stock_export",
    ),
    path(
        "movements/",
        MovementReportView.as_view(),
        name="movements_report",
    ),
    path(
        "movements/export/<str:export_format>/",
        MovementReportExportView.as_view(),
        name="movements_export",
    ),
]
