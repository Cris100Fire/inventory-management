from decimal import Decimal
from django.db.models import (
    DecimalField,
    ExpressionWrapper,
    F,
    Q,
    Sum,
    Case,
    IntegerField,
    Value,
    When,
)
from django.db.models.functions import Coalesce

from apps.catalog.models import Product
from apps.inventory.models import StockMovement


def get_stock_report_queryset(filters=None):
    filters = filters or {}

    queryset = Product.objects.select_related("category", "supplier")
    search = filters.get("search", "").strip()
    category = filters.get("category")
    supplier = filters.get("supplier")
    stock_status = filters.get("stock_status", "")
    active_status = filters.get("active_status") or "active"

    # Búsqueda por nombre o SKU:
    if search:
        queryset = queryset.filter(Q(name__icontains=search) | Q(sku__icontains=search))

    # Filtro de categoría
    if category:
        queryset = queryset.filter(category=category)

    # Filtro de proveedor
    if supplier:
        queryset = queryset.filter(supplier=supplier)

    # Estado del producto
    if active_status == "active":
        queryset = queryset.filter(is_active=True)

    elif active_status == "inactive":
        queryset = queryset.filter(is_active=False)

    # Estado del stock
    if stock_status == "out":
        queryset = queryset.filter(stock=0)

    elif stock_status == "low":
        queryset = queryset.filter(
            stock__gt=0,
            stock__lte=F("minimum_stock"),
        )

    elif stock_status == "available":
        queryset = queryset.filter(
            stock__gt=F("minimum_stock"),
        )

    # Valor estimado de las existencias
    queryset = queryset.annotate(
        stock_value=ExpressionWrapper(
            F("price") * F("stock"),
            output_field=DecimalField(
                max_digits=20,
                decimal_places=2,
            ),
        ),
    )

    return queryset.order_by("name", "pk")


def get_stock_report_summary(queryset):
    summary = queryset.aggregate(
        total_units=Coalesce(
            Sum("stock"),
            0,
        ),
        total_value=Coalesce(
            Sum("stock_value"),
            Decimal("0.00"),
            output_field=DecimalField(
                max_digits=24,
                decimal_places=2,
            ),
        ),
    )

    return {
        "total_products": queryset.count(),
        "total_units": summary["total_units"],
        "total_value": summary["total_value"],
        "out_of_stock": queryset.filter(stock=0).count(),
        "low_stock": queryset.filter(
            stock__gt=0,
            stock__lte=F("minimum_stock"),
        ).count(),
    }


def get_low_stock_report_queryset(filters=None):
    filters = filters or {}
    stock_status = filters.get("stock_status", "")

    base_filters = {
        **filters,
        "stock_status": "",
    }

    queryset = get_stock_report_queryset(base_filters)

    if stock_status == "out":
        return queryset.filter(stock=0)

    if stock_status == "low":
        return queryset.filter(
            stock__gt=0,
            stock__lte=F("minimum_stock"),
        )

    return queryset.filter(
        stock__lte=F("minimum_stock"),
    )


def get_movement_report_queryset(filters=None):
    filters = filters or {}

    queryset = StockMovement.objects.select_related(
        "product",
        "user",
        "supplier",
    )

    start_date = filters.get("start_date")
    end_date = filters.get("end_date")
    product = filters.get("product")
    movement_type = filters.get("movement_type")
    user = filters.get("user")

    if start_date:
        queryset = queryset.filter(created_at__date__gte=start_date)

    if end_date:
        queryset = queryset.filter(created_at__date__lte=end_date)

    if product:
        queryset = queryset.filter(product=product)

    if movement_type:
        queryset = queryset.filter(movement_type=movement_type)

    if user:
        queryset = queryset.filter(user=user)

    return queryset.order_by("-created_at", "-pk")


def get_movement_report_summary(queryset):
    entries = queryset.filter(
        movement_type__in=[
            StockMovement.MovementType.ENTRY,
            StockMovement.MovementType.ADJUSTMENT_IN,
        ]
    )

    exits = queryset.filter(
        movement_type__in=[
            StockMovement.MovementType.EXIT,
            StockMovement.MovementType.ADJUSTMENT_OUT,
        ]
    )

    total_entries = entries.aggregate(total=Sum("quantity"))["total"] or 0

    total_exits = exits.aggregate(total=Sum("quantity"))["total"] or 0

    return {
        "total_movements": queryset.count(),
        "total_entries": total_entries,
        "total_exits": total_exits,
        "net_balance": total_entries - total_exits,
    }
