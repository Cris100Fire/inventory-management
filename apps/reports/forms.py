from django import forms
from typing import cast
from django.contrib.auth import get_user_model

from apps.catalog.models import Category, Supplier, Product
from apps.inventory.models import StockMovement


class StockReportFilterForm(forms.Form):
    STOCK_STATUS_CHOICES = [
        ("", "Todos los estados"),
        ("available", "Disponible"),
        ("low", "Stock bajo"),
        ("out", "Agotado"),
    ]

    ACTIVE_STATUS_CHOICES = [
        ("active", "Solo activos"),
        ("inactive", "Solo inactivos"),
        ("all", "Todos los productos"),
    ]

    search = forms.CharField(
        required=False,
        label="Buscar producto",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Nombre o SKU",
            }
        ),
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        empty_label="Todas las categorías",
        label="Categoría",
    )

    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.none(),
        required=False,
        empty_label="Todos los proveedores",
        label="Proveedor",
    )

    stock_status = forms.ChoiceField(
        choices=STOCK_STATUS_CHOICES,
        required=False,
        label="Estado del stock",
    )

    active_status = forms.ChoiceField(
        choices=ACTIVE_STATUS_CHOICES,
        required=False,
        initial="active",
        label="Estado del producto",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        category_field = cast(
            forms.ModelChoiceField,
            self.fields["category"],
        )

        supplier_field = cast(
            forms.ModelChoiceField,
            self.fields["supplier"],
        )

        category_field.queryset = Category.objects.order_by("name")
        supplier_field.queryset = Supplier.objects.order_by("name")


class LowStockReportFilterForm(StockReportFilterForm):
    STOCK_STATUS_CHOICES = [
        ("", "Stock bajo y agotados"),
        ("low", "Solo stock bajo"),
        ("out", "Solo agotados"),
    ]

    stock_status = forms.ChoiceField(
        choices=STOCK_STATUS_CHOICES,
        required=False,
        label="Estado del stock",
    )


class MovementReportFilterForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        label="Fecha desde",
        widget=forms.DateInput(
            attrs={"type": "date"},
            format="%Y-%m-%d",
        ),
    )

    end_date = forms.DateField(
        required=False,
        label="Fecha hasta",
        widget=forms.DateInput(
            attrs={"type": "date"},
            format="%Y-%m-%d",
        ),
    )

    product = forms.ModelChoiceField(
        queryset=Product.objects.none(),
        required=False,
        empty_label="Todos los productos",
        label="Producto",
    )

    movement_type = forms.ChoiceField(
        choices=[
            ("", "Todos los movimientos"),
            *StockMovement.MovementType.choices,
        ],
        required=False,
        label="Tipo de movimiento",
    )

    user = forms.ModelChoiceField(
        queryset=get_user_model().objects.none(),
        required=False,
        empty_label="Todos los usuarios",
        label="Usuario",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        from typing import cast

        product_field = cast(
            forms.ModelChoiceField,
            self.fields["product"],
        )

        user_field = cast(
            forms.ModelChoiceField,
            self.fields["user"],
        )

        product_field.queryset = Product.objects.order_by("name")

        user_field.queryset = get_user_model().objects.order_by("username")

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and start_date > end_date:
            self.add_error(
                "end_date",
                "La fecha final no puede ser anterior a la inicial.",
            )

        return cleaned_data
