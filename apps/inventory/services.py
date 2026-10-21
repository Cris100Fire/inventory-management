from django.core.exceptions import ValidationError
from django.db import transaction

from apps.catalog.models import Product
from .models import StockMovement


@transaction.atomic
def register_stock_movement(
    *, product_id, movement_type, quantity, user, supplier=None, notes=""
):
    if quantity <= 0:
        raise ValidationError("La cantidad debe ser mayor que cero.")

    valid_types = StockMovement.MovementType.values

    if movement_type not in valid_types:
        raise ValidationError("El tipo de movimiento no es válido.")

    product = Product.objects.select_for_update().get(pk=product_id)

    if not product.is_active:
        raise ValidationError(
            "No se pueden registrar movimientos para un producto inactivo."
        )

    outgoing_types = (
        StockMovement.MovementType.EXIT,
        StockMovement.MovementType.ADJUSTMENT_OUT,
    )

    if movement_type in outgoing_types:
        if product.stock < quantity:
            raise ValidationError("No hay suficiente stock para la salida.")

        product.stock -= quantity
    else:
        product.stock += quantity

    product.save(update_fields=["stock"])

    movement = StockMovement.objects.create(
        product=product,
        movement_type=movement_type,
        quantity=quantity,
        user=user,
        supplier=supplier,
        notes=notes,
    )

    return movement
