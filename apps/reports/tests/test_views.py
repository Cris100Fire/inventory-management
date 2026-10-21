from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from apps.catalog.models import Category, Product
from apps.inventory.models import StockMovement


class ReportViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):

        User = get_user_model()

        # ==========================================
        # USUARIOS
        # ==========================================

        cls.admin_user = User.objects.create_user(
            username="reports_admin",
            password="TestPassword123!",
        )

        cls.consult_user = User.objects.create_user(
            username="reports_consult",
            password="TestPassword123!",
        )

        cls.no_permission_user = User.objects.create_user(
            username="reports_no_permission",
            password="TestPassword123!",
        )

        # Permisos necesarios para consultar reportes.
        product_permission = Permission.objects.get(
            codename="view_product",
            content_type__app_label="catalog",
        )

        movement_permission = Permission.objects.get(
            codename="view_stockmovement",
            content_type__app_label="inventory",
        )

        cls.admin_user.user_permissions.add(
            product_permission,
            movement_permission,
        )

        cls.consult_user.user_permissions.add(
            product_permission,
        )

        # ==========================================
        # DATOS DE PRUEBA
        # ==========================================

        cls.category = Category.objects.create(
            name="Categoría vistas",
        )

        cls.available = Product.objects.create(
            name="Teclado vistas",
            sku="VIEW-001",
            price=Decimal("50.00"),
            stock=20,
            minimum_stock=5,
            category=cls.category,
        )

        cls.low_stock = Product.objects.create(
            name="Mouse vistas",
            sku="VIEW-002",
            price=Decimal("25.00"),
            stock=3,
            minimum_stock=5,
            category=cls.category,
        )

        cls.out_of_stock = Product.objects.create(
            name="Monitor vistas",
            sku="VIEW-003",
            price=Decimal("400.00"),
            stock=0,
            minimum_stock=5,
            category=cls.category,
        )

        cls.entry = StockMovement.objects.create(
            product=cls.available,
            movement_type=StockMovement.MovementType.ENTRY,
            quantity=10,
            user=cls.admin_user,
            notes="Entrada de prueba",
        )

        cls.exit = StockMovement.objects.create(
            product=cls.low_stock,
            movement_type=StockMovement.MovementType.EXIT,
            quantity=2,
            user=cls.admin_user,
            notes="Salida de prueba",
        )

    # ==========================================
    # AUTENTICACIÓN
    # ==========================================

    def test_stock_report_requires_login(self):

        response = self.client.get(reverse("reports:stock_report"))

        self.assertEqual(response.status_code, 302)

    def test_low_stock_report_requires_login(self):

        response = self.client.get(reverse("reports:low_stock_report"))

        self.assertEqual(response.status_code, 302)

    def test_movement_report_requires_login(self):

        response = self.client.get(reverse("reports:movements_report"))

        self.assertEqual(response.status_code, 302)

    # ==========================================
    # PERMISOS
    # ==========================================

    def test_stock_report_denies_user_without_permission(self):

        self.client.force_login(self.no_permission_user)

        response = self.client.get(reverse("reports:stock_report"))

        self.assertEqual(response.status_code, 403)

    def test_low_stock_report_denies_user_without_permission(self):

        self.client.force_login(self.no_permission_user)

        response = self.client.get(reverse("reports:low_stock_report"))

        self.assertEqual(response.status_code, 403)

    def test_movement_report_denies_user_without_permission(self):

        self.client.force_login(self.no_permission_user)

        response = self.client.get(reverse("reports:movements_report"))

        self.assertEqual(response.status_code, 403)

    def test_user_with_product_permission_cannot_view_movements(self):

        self.client.force_login(self.consult_user)

        response = self.client.get(reverse("reports:movements_report"))

        self.assertEqual(response.status_code, 403)

    def test_user_with_product_permission_can_view_stock(self):

        self.client.force_login(self.consult_user)

        response = self.client.get(reverse("reports:stock_report"))

        self.assertEqual(response.status_code, 200)

    # ==========================================
    # REPORTE DE EXISTENCIAS
    # ==========================================

    def test_stock_report_loads_correctly(self):

        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("reports:stock_report"))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "reports/stock_report.html",
        )

        self.assertEqual(
            response.context["summary"]["total_products"],
            3,
        )

    def test_stock_report_search_filter(self):

        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse("reports:stock_report"),
            {"search": "Teclado"},
        )

        self.assertEqual(response.status_code, 200)

        products = response.context["products"]

        self.assertEqual(len(products), 1)

        self.assertEqual(
            products[0],
            self.available,
        )

    def test_stock_report_out_of_stock_filter(self):

        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse("reports:stock_report"),
            {"stock_status": "out"},
        )

        products = response.context["products"]

        self.assertEqual(len(products), 1)

        self.assertEqual(
            products[0],
            self.out_of_stock,
        )

    # ==========================================
    # REPORTE DE STOCK BAJO
    # ==========================================

    def test_low_stock_report_loads_correctly(self):

        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("reports:low_stock_report"))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "reports/low_stock_report.html",
        )

    def test_low_stock_report_only_critical_products(self):

        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("reports:low_stock_report"))

        products = list(response.context["products"])

        self.assertEqual(len(products), 2)

        self.assertIn(
            self.low_stock,
            products,
        )

        self.assertIn(
            self.out_of_stock,
            products,
        )

        self.assertNotIn(
            self.available,
            products,
        )

    # ==========================================
    # REPORTE DE MOVIMIENTOS
    # ==========================================

    def test_movement_report_loads_correctly(self):

        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("reports:movements_report"))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "reports/movements_report.html",
        )

        self.assertEqual(
            response.context["summary"]["total_movements"],
            2,
        )

    def test_movement_report_filters_by_type(self):

        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse("reports:movements_report"),
            {
                "movement_type": (StockMovement.MovementType.ENTRY),
            },
        )

        movements = list(response.context["movements"])

        self.assertEqual(len(movements), 1)

        self.assertEqual(
            movements[0],
            self.entry,
        )

    def test_movement_report_filters_by_user(self):

        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse("reports:movements_report"),
            {
                "user": self.admin_user.pk,
            },
        )

        movements = response.context["movements"]

        self.assertEqual(len(movements), 2)

    # ==========================================
    # PAGINACIÓN
    # ==========================================

    def test_stock_report_pagination(self):

        for index in range(25):

            Product.objects.create(
                name=f"Producto paginación {index}",
                sku=f"PAGE-{index:03d}",
                price=Decimal("10.00"),
                stock=10,
                minimum_stock=2,
                category=self.category,
            )

        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("reports:stock_report"))

        page_obj = response.context["page_obj"]

        self.assertEqual(
            len(page_obj.object_list),
            20,
        )

        self.assertEqual(
            page_obj.paginator.num_pages,
            2,
        )

    def test_stock_report_second_page(self):

        for index in range(25):

            Product.objects.create(
                name=f"Producto segunda página {index}",
                sku=f"PAGE2-{index:03d}",
                price=Decimal("10.00"),
                stock=10,
                minimum_stock=2,
                category=self.category,
            )

        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse("reports:stock_report"),
            {"page": 2},
        )

        page_obj = response.context["page_obj"]

        self.assertEqual(
            page_obj.number,
            2,
        )

        self.assertEqual(
            len(page_obj.object_list),
            8,
        )

    # ==========================================
    # EXPORTACIONES CSV
    # ==========================================

    def test_stock_csv_export_response(self):

        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse(
                "reports:stock_export",
                args=["csv"],
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertIn(
            "text/csv",
            response["Content-Type"],
        )

        self.assertIn(
            "reporte_existencias.csv",
            response["Content-Disposition"],
        )

    def test_low_stock_csv_export_response(self):

        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse(
                "reports:low_stock_export",
                args=["csv"],
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertIn(
            "reporte_stock_bajo.csv",
            response["Content-Disposition"],
        )

    def test_movement_csv_export_response(self):

        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse(
                "reports:movements_export",
                args=["csv"],
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertIn(
            "reporte_movimientos.csv",
            response["Content-Disposition"],
        )

    # ==========================================
    # EXPORTACIONES EXCEL
    # ==========================================

    def test_stock_excel_export_response(self):

        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse(
                "reports:stock_export",
                args=["xlsx"],
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertIn(
            "reporte_existencias.xlsx",
            response["Content-Disposition"],
        )

    def test_low_stock_excel_export_response(self):

        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse(
                "reports:low_stock_export",
                args=["xlsx"],
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertIn(
            "reporte_stock_bajo.xlsx",
            response["Content-Disposition"],
        )

    def test_movement_excel_export_response(self):

        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse(
                "reports:movements_export",
                args=["xlsx"],
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertIn(
            "reporte_movimientos.xlsx",
            response["Content-Disposition"],
        )

    # ==========================================
    # SEGURIDAD DE EXPORTACIONES
    # ==========================================

    def test_export_requires_login(self):

        response = self.client.get(
            reverse(
                "reports:stock_export",
                args=["csv"],
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_export_denies_user_without_permission(self):

        self.client.force_login(self.no_permission_user)

        response = self.client.get(
            reverse(
                "reports:stock_export",
                args=["csv"],
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_movement_export_denies_user_without_permission(self):

        self.client.force_login(self.consult_user)

        response = self.client.get(
            reverse(
                "reports:movements_export",
                args=["xlsx"],
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_invalid_export_format(self):

        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse(
                "reports:stock_export",
                args=["pdf"],
            )
        )

        self.assertEqual(response.status_code, 400)

    def test_invalid_movement_date_filter(self):

        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse(
                "reports:movements_export",
                args=["csv"],
            ),
            {
                "start_date": "2026-10-20",
                "end_date": "2026-10-01",
            },
        )

        self.assertEqual(response.status_code, 400)
