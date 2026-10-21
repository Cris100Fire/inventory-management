from typing import cast
from django import forms
from django.forms import ModelChoiceField

from apps.catalog.models import Product, Supplier
from .models import StockMovement


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = [
            "product",
            "movement_type",
            "quantity",
            "supplier",
            "notes",
        ]
        labels = {
            "product": "Producto",
            "movement_type": "Tipo de movimiento",
            "quantity": "Cantidad",
            "supplier": "Proveedor",
            "notes": "Observaciones",
        }
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        product_field = cast(
            ModelChoiceField,
            self.fields["product"],
        )
        product_field.queryset = Product.objects.filter(is_active=True).order_by("name")

        supplier_field = cast(ModelChoiceField, self.fields["supplier"])
        supplier_field.queryset = Supplier.objects.filter(is_active=True).order_by(
            "name"
        )
        supplier_field.required = False

        self.fields["notes"].required = False

    def clean(self):
        cleaned_data = super().clean()
        movement_type = cleaned_data.get("movement_type")
        notes = cleaned_data.get("notes")

        adjustment_types = (
            StockMovement.MovementType.ADJUSTMENT_IN,
            StockMovement.MovementType.ADJUSTMENT_OUT,
        )

        if movement_type in adjustment_types and not (notes or "").strip():
            self.add_error("notes", "Debes indicar el motivo del ajuste de inventario.")

        return cleaned_data
