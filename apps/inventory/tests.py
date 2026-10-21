from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from unittest.mock import patch

from apps.catalog.models import Category, Product
from apps.inventory.models import StockMovement
from apps.inventory.services import register_stock_movement

User = get_user_model()


class RegisterStockMovementTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test_user",
            password="test_password",
        )

        self.category = Category.objects.create(
            name="Test category",
        )

        self.product = Product.objects.create(
            sku="TEST-001",
            name="Test product",
            price=Decimal("10.00"),
            category=self.category,
            stock=8,
        )

    def test_entry_increases_stock(self):
        movement = register_stock_movement(
            product_id=self.product.pk,
            movement_type=StockMovement.MovementType.ENTRY,
            quantity=5,
            user=self.user,
        )

        self.product.refresh_from_db()

        self.assertEqual(self.product.stock, 13)
        self.assertEqual(movement.quantity, 5)
        self.assertEqual(
            StockMovement.objects.count(),
            1,
        )

    def test_exit_decreases_stock(self):
        register_stock_movement(
            product_id=self.product.pk,
            movement_type=StockMovement.MovementType.EXIT,
            quantity=3,
            user=self.user,
        )

        self.product.refresh_from_db()

        self.assertEqual(self.product.stock, 5)
        self.assertEqual(
            StockMovement.objects.count(),
            1,
        )

    def test_exit_cannot_exceed_available_stock(self):
        with self.assertRaises(ValidationError):
            register_stock_movement(
                product_id=self.product.pk,
                movement_type=StockMovement.MovementType.EXIT,
                quantity=10,
                user=self.user,
            )

        self.product.refresh_from_db()

        self.assertEqual(self.product.stock, 8)
        self.assertEqual(
            StockMovement.objects.count(),
            0,
        )

    def test_zero_quantity_is_rejected(self):
        with self.assertRaises(ValidationError):
            register_stock_movement(
                product_id=self.product.pk,
                movement_type=StockMovement.MovementType.ENTRY,
                quantity=0,
                user=self.user,
            )

        self.product.refresh_from_db()

        self.assertEqual(self.product.stock, 8)
        self.assertEqual(
            StockMovement.objects.count(),
            0,
        )

    def test_adjustment_in_increases_stock(self):
        register_stock_movement(
            product_id=self.product.pk,
            movement_type=StockMovement.MovementType.ADJUSTMENT_IN,
            quantity=4,
            user=self.user,
        )

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 12)

    def test_adjustment_out_decreases_stock(self):
        register_stock_movement(
            product_id=self.product.pk,
            movement_type=StockMovement.MovementType.ADJUSTMENT_OUT,
            quantity=3,
            user=self.user,
        )

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)

    def test_invalid_movement_type_is_rejected(self):
        with self.assertRaises(ValidationError):
            register_stock_movement(
                product_id=self.product.pk,
                movement_type="INVALID",
                quantity=1,
                user=self.user,
            )

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)
        self.assertEqual(StockMovement.objects.count(), 0)

    def test_nonexistent_product_is_rejected(self):
        with self.assertRaises(Product.DoesNotExist):
            register_stock_movement(
                product_id=999999,
                movement_type=StockMovement.MovementType.ENTRY,
                quantity=5,
                user=self.user,
            )

        self.assertEqual(StockMovement.objects.count(), 0)

    def test_stock_is_rolled_back_if_movement_creation_fails(self):
        with patch(
            "apps.inventory.services.StockMovement.objects.create",
            side_effect=Exception("Simulated database error"),
        ):
            with self.assertRaises(Exception):
                register_stock_movement(
                    product_id=self.product.pk,
                    movement_type=StockMovement.MovementType.ENTRY,
                    quantity=5,
                    user=self.user,
                )

        self.product.refresh_from_db()

        self.assertEqual(self.product.stock, 8)
        self.assertEqual(StockMovement.objects.count(), 0)
