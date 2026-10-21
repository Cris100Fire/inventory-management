from django import forms

from .models import Product, Category, Supplier


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "sku",
            "description",
            "price",
            "minimum_stock",
            "category",
            "supplier",
            "is_active",
        ]

        labels = {
            "name": "Nombre del producto",
            "sku": "Código SKU",
            "description": "Descripción",
            "price": "Precio",
            "minimum_stock": "Stock mínimo",
            "category": "Categoría",
            "supplier": "Proveedor",
            "is_active": "Producto activo",
        }

        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "price": forms.NumberInput(attrs={"step": "0.01"}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            "name",
            "description",
            "is_active",
        ]
        labels = {
            "name": "Nombre de la categoría",
            "description": "Descripción",
            "is_active": "Categoría activa",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            "name",
            "tax_id",
            "phone",
            "email",
            "is_active",
        ]
        labels = {
            "name": "Nombre del proveedor",
            "tax_id": "RUC",
            "phone": "Teléfono",
            "email": "Correo electrónico",
            "is_active": "Proveedor activo",
        }
