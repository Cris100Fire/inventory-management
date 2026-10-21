from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class StockMovement(models.Model):
    class MovementType(models.TextChoices):
        ENTRY = "ENTRY", "Entrada"
        EXIT = "EXIT", "Salida"
        ADJUSTMENT_IN = "ADJUSTMENT_IN", "Ajuste de entrada"
        ADJUSTMENT_OUT = "ADJUSTMENT_OUT", "Ajuste de salida"

    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.PROTECT,
        related_name="movements",
    )
    movement_type = models.CharField(max_length=20, choices=MovementType.choices)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    supplier = models.ForeignKey(
        "catalog.Supplier", on_delete=models.SET_NULL, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
