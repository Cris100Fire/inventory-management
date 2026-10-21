from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db import models

from apps.catalog.models import Category, Product, Supplier
from apps.inventory.models import StockMovement


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["total_products"] = Product.objects.filter(is_active=True).count()

        low_stock_queryset = (
            Product.objects.filter(is_active=True, stock__lte=models.F("minimum_stock"))
            .select_related("category", "supplier")
            .order_by("stock", "name")
        )

        context["low_stock_products"] = low_stock_queryset.count()
        context["low_stock_items"] = low_stock_queryset[:10]

        context["total_categories"] = Category.objects.filter(is_active=True).count()

        context["total_suppliers"] = Supplier.objects.filter(is_active=True).count()

        context["recent_movements"] = StockMovement.objects.select_related(
            "product", "user", "supplier"
        ).order_by("-created_at", "-pk")[:5]

        return context
