from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from datetime import date, timedelta
from django.utils import timezone

from apps.catalog.models import Category, Product, Supplier
from apps.reports.forms import StockReportFilterForm

from apps.reports.services.queries import (
    get_stock_report_queryset,
    get_stock_report_summary,
    get_low_stock_report_queryset,
    get_movement_report_queryset,
    get_movement_report_summary,
)

from apps.inventory.models import StockMovement


class StockReportQueryTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="Electrónica",
        )

        cls.other_category = Category.objects.create(
            name="Oficina",
        )

        cls.supplier = Supplier.objects.create(
            name="Proveedor Principal",
        )

        cls.available = Product.objects.create(
            name="Teclado",
            sku="TEC-001",
            price=Decimal("50.00"),
            stock=20,
            minimum_stock=5,
            category=cls.category,
            supplier=cls.supplier,
        )

        cls.low = Product.objects.create(
            name="Mouse",
            sku="MOU-001",
            price=Decimal("25.00"),
            stock=3,
            minimum_stock=5,
            category=cls.category,
            supplier=cls.supplier,
        )

        cls.out = Product.objects.create(
            name="Monitor",
            sku="MON-001",
            price=Decimal("400.00"),
            stock=0,
            minimum_stock=2,
            category=cls.category,
        )

        cls.inactive = Product.objects.create(
            name="Impresora",
            sku="IMP-001",
            price=Decimal("200.00"),
            stock=4,
            minimum_stock=2,
            category=cls.other_category,
            is_active=False,
        )

    def test_default_returns_only_active_products(self):
        queryset = get_stock_report_queryset()

        self.assertEqual(queryset.count(), 3)
        self.assertNotIn(self.inactive, queryset)

    def test_search_by_name(self):
        queryset = get_stock_report_queryset(
            {
                "search": "Teclado",
            }
        )

        self.assertEqual(list(queryset), [self.available])

    def test_search_by_sku(self):
        queryset = get_stock_report_queryset(
            {
                "search": "MOU-001",
            }
        )

        self.assertEqual(list(queryset), [self.low])

    def test_filter_by_category(self):
        queryset = get_stock_report_queryset(
            {
                "category": self.category,
            }
        )

        self.assertEqual(queryset.count(), 3)

    def test_filter_by_supplier(self):
        queryset = get_stock_report_queryset(
            {
                "supplier": self.supplier,
            }
        )

        self.assertEqual(queryset.count(), 2)

    def test_filter_available(self):
        queryset = get_stock_report_queryset(
            {
                "stock_status": "available",
            }
        )

        self.assertEqual(list(queryset), [self.available])

    def test_filter_low_stock(self):
        queryset = get_stock_report_queryset(
            {
                "stock_status": "low",
            }
        )

        self.assertEqual(list(queryset), [self.low])

    def test_filter_out_of_stock(self):
        queryset = get_stock_report_queryset(
            {
                "stock_status": "out",
            }
        )

        self.assertEqual(list(queryset), [self.out])

    def test_include_inactive_products(self):
        queryset = get_stock_report_queryset(
            {
                "active_status": "all",
            }
        )

        self.assertEqual(queryset.count(), 4)

    def test_only_inactive_products(self):
        queryset = get_stock_report_queryset(
            {
                "active_status": "inactive",
            }
        )

        self.assertEqual(list(queryset), [self.inactive])

    def test_stock_value_annotation(self):
        queryset = get_stock_report_queryset()

        product = queryset.get(pk=self.available.pk)

        self.assertEqual(
            getattr(product, "stock_value"),
            Decimal("1000.00"),
        )

    def test_summary(self):
        queryset = get_stock_report_queryset()

        summary = get_stock_report_summary(queryset)

        self.assertEqual(summary["total_products"], 3)
        self.assertEqual(summary["total_units"], 23)
        self.assertEqual(
            summary["total_value"],
            Decimal("1075.00"),
        )
        self.assertEqual(summary["out_of_stock"], 1)
        self.assertEqual(summary["low_stock"], 1)

    def test_invalid_category_is_rejected(self):
        form = StockReportFilterForm(data={"category": "999999"})

        self.assertFalse(form.is_valid())
        self.assertIn("category", form.errors)


class LowStockReportQueryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="Periféricos de prueba",
        )

        cls.available = Product.objects.create(
            name="Teclado disponible",
            sku="LOW-001",
            price=50,
            stock=20,
            minimum_stock=5,
            category=cls.category,
        )

        cls.low_stock = Product.objects.create(
            name="Mouse con stock bajo",
            sku="LOW-002",
            price=25,
            stock=3,
            minimum_stock=5,
            category=cls.category,
        )

        cls.out_of_stock = Product.objects.create(
            name="Monitor agotado",
            sku="LOW-003",
            price=400,
            stock=0,
            minimum_stock=5,
            category=cls.category,
        )

        cls.zero_minimum = Product.objects.create(
            name="Producto mínimo cero",
            sku="LOW-004",
            price=15,
            stock=0,
            minimum_stock=0,
            category=cls.category,
        )

    def test_only_critical_products_are_returned(self):
        queryset = get_low_stock_report_queryset()

        self.assertNotIn(self.available, queryset)
        self.assertIn(self.low_stock, queryset)
        self.assertIn(self.out_of_stock, queryset)

    def test_low_stock_filter_excludes_out_of_stock(self):
        queryset = get_low_stock_report_queryset(
            {
                "stock_status": "low",
            }
        )

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.low_stock)

    def test_out_of_stock_filter(self):
        queryset = get_low_stock_report_queryset(
            {
                "stock_status": "out",
            }
        )

        self.assertEqual(queryset.count(), 2)
        self.assertIn(self.out_of_stock, queryset)
        self.assertIn(self.zero_minimum, queryset)

    def test_zero_stock_with_zero_minimum_is_critical(self):
        queryset = get_low_stock_report_queryset()

        self.assertIn(self.zero_minimum, queryset)

    def test_search_filter(self):
        queryset = get_low_stock_report_queryset(
            {
                "search": "Mouse",
            }
        )

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.low_stock)


class MovementReportQueryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        cls.user1 = User.objects.create_user(
            username="report_user_1",
            password="TestPassword123!",
        )

        cls.user2 = User.objects.create_user(
            username="report_user_2",
            password="TestPassword123!",
        )

        cls.category = Category.objects.create(
            name="Categoría de movimientos",
        )

        cls.product1 = Product.objects.create(
            name="Producto movimientos A",
            sku="MOV-001",
            price=100,
            stock=15,
            minimum_stock=5,
            category=cls.category,
        )

        cls.product2 = Product.objects.create(
            name="Producto movimientos B",
            sku="MOV-002",
            price=200,
            stock=10,
            minimum_stock=3,
            category=cls.category,
        )

        cls.entry = StockMovement.objects.create(
            product=cls.product1,
            movement_type=StockMovement.MovementType.ENTRY,
            quantity=10,
            user=cls.user1,
        )

        cls.exit = StockMovement.objects.create(
            product=cls.product1,
            movement_type=StockMovement.MovementType.EXIT,
            quantity=4,
            user=cls.user2,
        )

        cls.adjustment_in = StockMovement.objects.create(
            product=cls.product2,
            movement_type=StockMovement.MovementType.ADJUSTMENT_IN,
            quantity=3,
            user=cls.user1,
        )

        cls.adjustment_out = StockMovement.objects.create(
            product=cls.product2,
            movement_type=StockMovement.MovementType.ADJUSTMENT_OUT,
            quantity=2,
            user=cls.user2,
        )

    def test_returns_all_movements(self):
        queryset = get_movement_report_queryset()

        self.assertEqual(queryset.count(), 4)

    def test_filter_by_product(self):
        queryset = get_movement_report_queryset(
            {
                "product": self.product1,
            }
        )

        self.assertEqual(queryset.count(), 2)

    def test_filter_by_user(self):
        queryset = get_movement_report_queryset(
            {
                "user": self.user1,
            }
        )

        self.assertEqual(queryset.count(), 2)

    def test_filter_by_movement_type(self):
        queryset = get_movement_report_queryset(
            {
                "movement_type": StockMovement.MovementType.EXIT,
            }
        )

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.exit)

    def test_summary_calculations(self):
        queryset = get_movement_report_queryset()

        summary = get_movement_report_summary(queryset)

        self.assertEqual(summary["total_movements"], 4)
        self.assertEqual(summary["total_entries"], 13)
        self.assertEqual(summary["total_exits"], 6)
        self.assertEqual(summary["net_balance"], 7)

    def test_summary_respects_filters(self):
        queryset = get_movement_report_queryset(
            {
                "product": self.product1,
            }
        )

        summary = get_movement_report_summary(queryset)

        self.assertEqual(summary["total_movements"], 2)
        self.assertEqual(summary["total_entries"], 10)
        self.assertEqual(summary["total_exits"], 4)
        self.assertEqual(summary["net_balance"], 6)

    def test_movements_are_ordered_newest_first(self):
        queryset = get_movement_report_queryset()

        self.assertEqual(
            list(queryset),
            [
                self.adjustment_out,
                self.adjustment_in,
                self.exit,
                self.entry,
            ],
        )

    def test_filter_by_start_date(self):
        today = timezone.localdate()

        queryset = get_movement_report_queryset(
            {
                "start_date": today,
            }
        )

        self.assertEqual(queryset.count(), 4)

    def test_filter_by_end_date_excludes_recent_movements(self):
        yesterday = date.today() - timedelta(days=1)

        queryset = get_movement_report_queryset(
            {
                "end_date": yesterday,
            }
        )

        self.assertEqual(queryset.count(), 0)
